"""
ChatKit Server implementation with MCP tools integration.
Integrates Gemini AI with database-backed conversation storage.
"""

import os
import json
import logging
from typing import AsyncIterator, List
from datetime import datetime, timezone
from pathlib import Path

from chatkit.server import ChatKitServer
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    AssistantMessageItem,
    ThreadItemAddedEvent,
    UserMessageContent,
    AssistantMessageContent,
    Page,
)
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from chatkit_store import DatabaseChatKitStore
from mcp_server.server import mcp

logger = logging.getLogger(__name__)

# Limit conversation history to avoid token limits and manage costs
MAX_RECENT_ITEMS = 30


class TodoChatKitServer(ChatKitServer):
    """ChatKit server with Gemini integration and MCP tools.

    Features:
    - Database-backed conversation storage
    - Gemini 2.0 Flash model
    - Multilingual support (English + Urdu)
    - MCP tools integration for task management
    """

    def __init__(self, store: DatabaseChatKitStore, api_key: str):
        super().__init__(store=store)

        # Configure Gemini client
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # Use correct Gemini model name
        self.model = OpenAIChatCompletionsModel(
            model="gemini-2.5-flash",
            openai_client=self.client
        )

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_path = Path(__file__).parent / "services" / "prompts" / "system_prompt.md"

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            # Fallback prompt if file not found
            content = """You are a helpful and efficient Todo Assistant.
Your goal is to help the user manage their tasks using the provided tools.

**Language & Persona:**
- You must strictly mirror the user's language.
- If the user speaks English, reply in English.
- If the user speaks Roman Urdu (e.g., "Task add kardo"), reply in Roman Urdu.
- If the user speaks Urdu Script, reply in Urdu Script.
- Keep responses concise and friendly.

**Tool Usage:**
- Use `add_task` to create new tasks.
- Use `list_tasks` to show tasks.
- Use `complete_task` to mark tasks as done.
- Use `delete_task` to remove tasks.
- Use `update_task` to modify tasks.
"""

        return content

    def _prepare_system_prompt(self, user_id: str) -> str:
        """Prepare system prompt with user context."""
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Replace placeholders
        prompt = self.system_prompt
        prompt = prompt.replace("{{user_id}}", user_id)
        prompt = prompt.replace("{{current_time}}", current_time)

        return prompt

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: str,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate streaming response to user message.

        Args:
            thread: Metadata for thread being processed
            input_user_message: The incoming user message (if any)
            context: User ID (context string)

        Yields:
            ThreadStreamEvent instances for streaming response
        """

        user_id = context
        thread_id = thread.id

        # Load conversation history (limited to recent items)
        items_page = await self.store.load_thread_items(
            thread_id=thread_id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="asc",
            context=user_id
        )
        items = items_page.data

        # Prepare system message with context
        system_message: ChatCompletionMessageParam = {
            "role": "system",
            "content": self._prepare_system_prompt(user_id)
        }

        # Convert thread items to OpenAI chat format
        chat_messages: list[ChatCompletionMessageParam] = [system_message]

        for item in items:
            if isinstance(item, UserMessageItem):
                # Extract text from user message
                text = ""
                for content in item.content:
                    if content.type == "text":
                        text = content.text
                        break
                if text:
                    chat_messages.append({"role": "user", "content": text})

            elif isinstance(item, AssistantMessageItem):
                # Extract text from assistant message
                text = ""
                for content in item.content:
                    if content.type == "text":
                        text = content.text
                        break
                if text:
                    chat_messages.append({"role": "assistant", "content": text})

        # Create assistant message for response
        assistant_id = self.store.generate_item_id("assistant_message", thread, user_id)
        assistant_item = AssistantMessageItem(
            id=assistant_id,
            thread_id=thread_id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(type="text", text="")]
        )

        yield ThreadItemAddedEvent(item=assistant_item)

        # Stream response from Gemini
        full_response = ""
        async for chunk in self.model.respond_stream(chat_messages):
            full_response += chunk

            # Update assistant message content
            assistant_item.content = [AssistantMessageContent(type="text", text=full_response)]
            yield ThreadItemAddedEvent(item=assistant_item)

        # Final update - message is complete
        assistant_item.content = [AssistantMessageContent(type="text", text=full_response)]


class TodoChatKitServerWithMCP(TodoChatKitServer):
    """Extended ChatKit server with MCP tools integration.

    This version integrates MCP tools directly into the ChatKit server
    for seamless task management within the chat interface.
    """

    def __init__(self, store: DatabaseChatKitStore, api_key: str, mcp_tools: list = None):
        super().__init__(store, api_key)
        self.mcp_tools = mcp_tools or []

    def _get_openai_tools(self) -> List[ChatCompletionToolParam]:
        """Convert MCP tools to OpenAI function calling schema.

        Fetches tools from MCP server and converts them to OpenAI format.
        Removes user_id from schema (injected server-side for security).
        """
        mcp_tools = mcp._tool_manager.list_tools()
        openai_tools: List[ChatCompletionToolParam] = []

        for tool in mcp_tools:
            # Deep copy to modify parameters
            tool_def = tool.model_dump()
            parameters = tool_def.get("parameters", {})

            # Remove user_id from properties and required (security: injected server-side)
            if "properties" in parameters and "user_id" in parameters["properties"]:
                del parameters["properties"]["user_id"]

            if "required" in parameters and "user_id" in parameters["required"]:
                parameters["required"].remove("user_id")

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": parameters
                }
            })

        return openai_tools

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: str,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate streaming response with MCP tools integration.

        Implements tool calling loop:
        1. Load conversation history
        2. Prepare messages for Gemini
        3. Call Gemini with MCP tools available
        4. Execute any tool calls
        5. Stream final response back to user
        """

        user_id = context
        thread_id = thread.id

        # Load conversation history (limited to recent items)
        items_page = await self.store.load_thread_items(
            thread_id=thread_id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="asc",
            context=user_id
        )
        items = items_page.data

        # Prepare system message with context
        system_message: ChatCompletionMessageParam = {
            "role": "system",
            "content": self._prepare_system_prompt(user_id)
        }

        # Convert thread items to OpenAI chat format
        chat_messages: list[ChatCompletionMessageParam] = [system_message]

        for item in items:
            if isinstance(item, UserMessageItem):
                # Extract text from user message
                text = ""
                for content in item.content:
                    if content.type == "text":
                        text = content.text
                        break
                if text:
                    chat_messages.append({"role": "user", "content": text})

            elif isinstance(item, AssistantMessageItem):
                # Extract text from assistant message
                text = ""
                for content in item.content:
                    if content.type == "text":
                        text = content.text
                        break
                if text:
                    chat_messages.append({"role": "assistant", "content": text})

        # Get MCP tools
        tools = self._get_openai_tools()

        # Tool calling loop (max 5 iterations to prevent infinite loops)
        final_response = ""
        for iteration in range(5):
            try:
                response = await self.client.chat.completions.create(
                    model="gemini-2.5-flash",  # Gemini 2.5 supports tool calling
                    messages=chat_messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None
                )

                response_message = response.choices[0].message
                chat_messages.append(response_message)

                if response_message.tool_calls:
                    # Execute tool calls
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        # Inject user_id (security: don't trust client)
                        arguments["user_id"] = user_id

                        logger.info(f"Executing MCP tool: {function_name} with args: {arguments}")

                        try:
                            # Execute MCP tool
                            result = await mcp.call_tool(function_name, arguments)
                            result_str = json.dumps(result, default=str)
                        except Exception as e:
                            logger.error(f"MCP tool execution failed: {e}")
                            result_str = json.dumps({"error": str(e)})

                        # Add tool result to messages
                        chat_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_str
                        })
                    # Continue loop to process tool results
                else:
                    # No more tool calls - we have the final response
                    final_response = response_message.content or ""
                    break

            except Exception as e:
                logger.error(f"Error during tool calling loop (iteration {iteration}): {e}")
                final_response = "I apologize, but I encountered an error processing your request. Please try again."
                break

        # Create assistant message for response
        assistant_id = self.store.generate_item_id("assistant_message", thread, user_id)
        assistant_item = AssistantMessageItem(
            id=assistant_id,
            thread_id=thread_id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(type="text", text="")]
        )

        yield ThreadItemAddedEvent(item=assistant_item)

        # Stream final response (simulate streaming word by word for better UX)
        words = final_response.split()
        streamed_text = ""
        for word in words:
            streamed_text += word + " "
            assistant_item.content = [AssistantMessageContent(type="text", text=streamed_text.strip())]
            yield ThreadItemAddedEvent(item=assistant_item)

        # Final update with complete message
        assistant_item.content = [AssistantMessageContent(type="text", text=final_response)]
