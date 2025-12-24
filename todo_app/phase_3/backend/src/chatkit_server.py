"""
ChatKit Server implementation with MCP tools integration.
Integrates Gemini AI with database-backed conversation storage.
"""

import os
from typing import AsyncIterator
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
from openai.types.chat import ChatCompletionMessageParam

from chatkit_store import DatabaseChatKitStore

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
            model="gemini-2.0-flash-exp",
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

    def __init__(self, store: DatabaseChatKitStore, api_key: str, mcp_tools: list):
        super().__init__(store, api_key)
        self.mcp_tools = mcp_tools

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: str,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate streaming response with MCP tools integration.

        Note: Full MCP tools integration requires additional implementation
        to map ChatKit tool calling to MCP protocol. For now, this extends
        the base implementation.
        """

        # TODO: Integrate MCP tools into the model call
        # This requires mapping OpenAI tool calling format to MCP protocol
        # For Phase 3, we use the base implementation

        # Stream responses using base implementation
        async for event in super().respond(thread, input_user_message, context):
            yield event
