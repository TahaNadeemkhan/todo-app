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
    WidgetItem,
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
                # ChatKit uses "input_text" for user messages, not "text"
                text = ""
                for content in item.content:
                    content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                    if content_type in ("text", "input_text"):
                        text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                        break
                if text:
                    chat_messages.append({"role": "user", "content": text})

            elif isinstance(item, AssistantMessageItem):
                # Extract text from assistant message
                text = ""
                for content in item.content:
                    content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                    if content_type == "text":
                        text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                        break
                if text:
                    chat_messages.append({"role": "assistant", "content": text})

        # If no messages from history, add the current input message directly
        if len(chat_messages) == 1 and input_user_message:
            # Only system message - add the current user message
            for content in input_user_message.content:
                content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                if content_type in ("text", "input_text"):
                    text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                    if text:
                        chat_messages.append({"role": "user", "content": text})
                        break

        logger.info(f"Prepared {len(chat_messages)} messages for Gemini API")

        # Create assistant message for response
        # Generate ID manually since store.generate_item_id has limited item types
        import uuid
        assistant_id = f"msg_{uuid.uuid4().hex[:8]}"
        assistant_item = AssistantMessageItem(
            id=assistant_id,
            thread_id=thread_id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(type="output_text", text="")]
        )

        yield ThreadItemAddedEvent(item=assistant_item)

        # Stream response from Gemini
        full_response = ""
        async for chunk in self.model.respond_stream(chat_messages):
            full_response += chunk

            # Update assistant message content
            assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
            yield ThreadItemAddedEvent(item=assistant_item)

        # Final update - message is complete
        assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]

        # ✅ SAVE assistant message to database
        await self.store.add_thread_item(thread_id, assistant_item, user_id)


class TodoChatKitServerWithMCP(TodoChatKitServer):
    """Extended ChatKit server with MCP tools integration.

    This version integrates MCP tools directly into the ChatKit server
    for seamless task management within the chat interface.
    """

    def __init__(self, store: DatabaseChatKitStore, api_key: str, mcp_tools: list = None):
        super().__init__(store, api_key)
        self.mcp_tools = mcp_tools or []

    async def action(
        self,
        thread: ThreadMetadata,
        action_type: str,
        payload: dict,
        context: str,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle widget actions (e.g., checkbox toggles)."""
        user_id = context
        logger.info(f"🎬 Widget action received: type={action_type}, payload={payload}")

        # Handle task toggle action (checkbox click)
        if action_type == "task.toggle":
            task_id = payload.get("id")
            if task_id:
                try:
                    # First, get current task state
                    logger.info(f"Toggling task {task_id}")
                    tasks_result = await mcp.call_tool("list_tasks", {
                        "status": "all",
                        "user_id": user_id
                    })

                    # Find the current task to check its completed status
                    current_completed = False
                    if isinstance(tasks_result, list) and len(tasks_result) > 0:
                        first_item = tasks_result[0]
                        if hasattr(first_item, 'text'):
                            task_data = json.loads(first_item.text)
                            for task in task_data.get("tasks", []):
                                if str(task.get("task_id")) == str(task_id):
                                    current_completed = task.get("completed", False)
                                    break

                    # Toggle: if currently completed, mark as pending; if pending, mark as completed
                    from repositories.task_repository import TaskRepository
                    from db import get_async_session

                    async for session in get_async_session():
                        repo = TaskRepository(session)
                        task = await repo.update(
                            task_id=int(task_id),
                            user_id=user_id,
                            completed=not current_completed
                        )
                        logger.info(f"✅ Task {task_id} toggled: {current_completed} -> {not current_completed}")

                    # Refresh the task list widget
                    logger.info(f"Refreshing task list after toggle")
                    tasks_result = await mcp.call_tool("list_tasks", {
                        "status": "all",
                        "user_id": user_id
                    })

                    # Parse and create new widget
                    if isinstance(tasks_result, list) and len(tasks_result) > 0:
                        first_item = tasks_result[0]
                        if hasattr(first_item, 'text'):
                            task_data = json.loads(first_item.text)
                            if "tasks" in task_data:
                                updated_widget = self._create_task_list_widget(task_data["tasks"])

                                # Yield updated widget
                                widget_id = f"widget_{uuid.uuid4().hex[:8]}"
                                widget_item = WidgetItem(
                                    id=widget_id,
                                    thread_id=thread.id,
                                    created_at=datetime.now(timezone.utc),
                                    type="widget",
                                    widget=updated_widget
                                )
                                yield ThreadItemAddedEvent(item=widget_item)
                                logger.info(f"✅ Refreshed widget after task toggle")

                except Exception as e:
                    logger.error(f"❌ Failed to toggle task: {e}")
        else:
            logger.warning(f"⚠️ Unknown action type: {action_type}")

        # Must be a generator - even if no events to yield
        return
        yield  # Make this an async generator

    def _create_task_list_widget(self, tasks: list) -> dict:
        """Convert task list to ChatKit widget JSON format.

        Uses the widget structure from ChatKit Studio Widget Builder.
        """
        if not tasks:
            return {
                "type": "Card",
                "size": "md",
                "status": {"text": "No tasks found"},
                "children": []
            }

        # Map priority to badge color
        priority_color_map = {
            "high": "danger",
            "medium": "warning",
            "low": "success"
        }

        list_view_items = []
        for task in tasks:
            task_id = task.get("task_id", "")
            title = task.get("title", "Untitled")
            description = task.get("description", "")
            completed = task.get("completed", False)
            priority = task.get("priority", "").lower()
            due_date = task.get("due_date")

            # Build children for each task item
            item_children = [
                {
                    "type": "Checkbox",
                    "name": f"tasks.{task_id}.done",
                    "defaultChecked": completed,
                    "onChangeAction": {
                        "type": "task.toggle",
                        "payload": {"id": task_id}
                    }
                },
                {
                    "type": "Col",
                    "flex": "auto",
                    "gap": 1,
                    "children": [
                        {
                            "type": "Text",
                            "value": title,
                            "weight": "bold",
                            "maxLines": 1
                        }
                    ]
                }
            ]

            # Add description if present
            if description:
                item_children[1]["children"].append({
                    "type": "Text",
                    "value": description,
                    "size": "sm",
                    "color": "secondary",
                    "maxLines": 2
                })

            # Add due date if present
            if due_date:
                try:
                    # Format date nicely
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(str(due_date).replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("Due %b %d")
                except:
                    formatted_date = f"Due {due_date}"

                item_children[1]["children"].append({
                    "type": "Row",
                    "gap": 1,
                    "children": [
                        {
                            "type": "Icon",
                            "name": "calendar",
                            "size": "sm",
                            "color": "secondary"
                        },
                        {
                            "type": "Caption",
                            "value": formatted_date,
                            "color": "secondary"
                        }
                    ]
                })

            # Add spacer
            item_children.append({"type": "Spacer"})

            # Add priority badge if present
            if priority and priority in priority_color_map:
                item_children.append({
                    "type": "Badge",
                    "label": priority.capitalize(),
                    "color": priority_color_map[priority]
                })

            # Create list view item
            list_view_items.append({
                "type": "ListViewItem",
                "key": task_id,
                "gap": 3,
                "children": item_children
            })

        # Build complete widget
        completed_count = sum(1 for t in tasks if t.get("completed", False))
        total_count = len(tasks)

        return {
            "type": "Card",
            "size": "md",
            "status": {
                "text": f"{completed_count}/{total_count} tasks completed"
            },
            "children": [
                {
                    "type": "ListView",
                    "children": list_view_items
                }
            ]
        }

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
                # ChatKit uses "input_text" for user messages, not "text"
                text = ""
                for content in item.content:
                    content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                    if content_type in ("text", "input_text"):
                        text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                        break
                if text:
                    chat_messages.append({"role": "user", "content": text})

            elif isinstance(item, AssistantMessageItem):
                # Extract text from assistant message
                text = ""
                for content in item.content:
                    content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                    if content_type == "text":
                        text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                        break
                if text:
                    chat_messages.append({"role": "assistant", "content": text})

        # If no messages from history, add the current input message directly
        if len(chat_messages) == 1 and input_user_message:
            # Only system message - add the current user message
            for content in input_user_message.content:
                content_type = getattr(content, 'type', None) or (content.get('type') if isinstance(content, dict) else None)
                if content_type in ("text", "input_text"):
                    text = getattr(content, 'text', None) or (content.get('text') if isinstance(content, dict) else "")
                    if text:
                        chat_messages.append({"role": "user", "content": text})
                        break

        logger.info(f"Prepared {len(chat_messages)} messages for Gemini API (MCP)")

        # Get MCP tools
        tools = self._get_openai_tools()
        logger.info(f"🔧 Available MCP tools: {len(tools)}")
        for tool in tools:
            logger.info(f"  - {tool['function']['name']}: {tool['function']['description']}")

        # Tool calling loop (max 5 iterations to prevent infinite loops)
        final_response = ""
        task_list_widget = None  # Will store widget if list_tasks is called

        for iteration in range(5):
            try:
                logger.info(f"🔄 Tool calling iteration {iteration + 1}")

                # Force tool usage on first iteration, then allow text responses
                # This ensures AI calls tools initially but can respond with text after tool results
                tool_choice_param = None
                if tools:
                    tool_choice_param = "required" if iteration == 0 else "auto"

                response = await self.client.chat.completions.create(
                    model="gemini-2.5-flash",  # Gemini 2.5 supports tool calling
                    messages=chat_messages,
                    tools=tools if tools else None,
                    tool_choice=tool_choice_param
                )

                logger.info(f"📥 Response finish_reason: {response.choices[0].finish_reason}")

                response_message = response.choices[0].message
                chat_messages.append(response_message)

                # Log tool calls status
                if response_message.tool_calls:
                    logger.info(f"🛠️ Tool calls detected: {len(response_message.tool_calls)}")
                else:
                    logger.info(f"💬 No tool calls - direct text response")
                    if response_message.content:
                        logger.info(f"   Response: {response_message.content[:100]}...")

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

                            # ✅ Capture list_tasks results for widget rendering
                            if function_name == "list_tasks":
                                logger.info(f"🔍 list_tasks result type: {type(result)}")

                                # Parse MCP result - it returns [TextContent(...)] format
                                task_data = None
                                if isinstance(result, list) and len(result) > 0:
                                    # Extract text from TextContent
                                    first_item = result[0]
                                    if hasattr(first_item, 'text'):
                                        json_str = first_item.text
                                        try:
                                            task_data = json.loads(json_str)
                                            logger.info(f"📋 Parsed task data: {len(task_data.get('tasks', []))} tasks")
                                        except json.JSONDecodeError as e:
                                            logger.error(f"Failed to parse JSON: {e}")
                                elif isinstance(result, dict):
                                    # Direct dict format (fallback)
                                    task_data = result

                                # Create widget if we have tasks
                                if task_data and "tasks" in task_data:
                                    logger.info(f"📋 Creating widget for {len(task_data['tasks'])} tasks")
                                    task_list_widget = self._create_task_list_widget(task_data["tasks"])
                                else:
                                    logger.warning(f"No tasks found in result")
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
        # Generate ID manually since store.generate_item_id has limited item types
        import uuid
        assistant_id = f"msg_{uuid.uuid4().hex[:8]}"
        assistant_item = AssistantMessageItem(
            id=assistant_id,
            thread_id=thread_id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(type="output_text", text="")]
        )

        yield ThreadItemAddedEvent(item=assistant_item)

        # Stream final response (simulate streaming word by word for better UX)
        words = final_response.split()
        streamed_text = ""
        for word in words:
            streamed_text += word + " "
            assistant_item.content = [AssistantMessageContent(type="output_text", text=streamed_text.strip())]
            yield ThreadItemAddedEvent(item=assistant_item)

        # Final update with complete message
        assistant_item.content = [AssistantMessageContent(type="output_text", text=final_response)]

        # ✅ SAVE assistant message to database
        await self.store.add_thread_item(thread_id, assistant_item, user_id)

        # ✅ If we have a task list widget, yield it as a separate message
        if task_list_widget:
            logger.info(f"📦 Yielding task list widget to client")
            widget_id = f"widget_{uuid.uuid4().hex[:8]}"
            widget_item = WidgetItem(
                id=widget_id,
                thread_id=thread_id,
                created_at=datetime.now(timezone.utc),
                type="widget",
                widget=task_list_widget
            )
            yield ThreadItemAddedEvent(item=widget_item)

            # Note: Widgets are ephemeral UI elements - not saved to database
            # They're generated on-the-fly from MCP tool results
