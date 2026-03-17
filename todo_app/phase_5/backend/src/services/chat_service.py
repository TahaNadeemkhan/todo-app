import json
import logging
import os
from uuid import UUID
from typing import List, Optional, Any, Dict
from datetime import datetime
from dotenv import load_dotenv

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message, MessageRole
from repositories.message_repository import MessageRepository
from services.conversation_state_service import ConversationStateService, MessageState
from mcp_server.server import mcp

load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # T058: Use Dapr State Store for conversation management (portable)
        self.conversation_service = ConversationStateService()
        self.message_repo = MessageRepository(session)
        
        # Configure OpenAI client for Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        if not api_key:
            # Fallback to standard OpenAI if GEMINI_API_KEY is missing but OPENAI_API_KEY exists
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = None  # Use default OpenAI endpoint
            self.model = "gpt-4o-mini"  # OpenAI model for fallback
        else:
            self.model = "gemini-2.5-flash"  # Gemini 2.0 Flash (supports tool calling)

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    async def process_message(
        self, 
        user_id: str, 
        message_content: str, 
        conversation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Process a user message, interact with OpenAI and MCP tools, and return the response.
        """
        # 1. Get or Create Conversation (T058: Using Dapr State Store)
        if conversation_id:
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                # Fallback to creating new if not found
                conversation = await self.conversation_service.create_conversation(user_id)
        else:
            conversation = await self.conversation_service.create_conversation(user_id)
        
        current_conversation_id = conversation.id

        # 2. Persist User Message (T058: Using Dapr State Store)
        await self.conversation_service.add_message(
            conversation_id=current_conversation_id,
            role="user",
            content=message_content
        )

        # 3. Load History (T058: From Dapr State Store)
        history = await self.conversation_service.get_conversation_history(current_conversation_id)
        
        # 4. Prepare Messages for OpenAI
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._get_system_prompt(user_id)}
        ]
        
        for msg in history:
            # msg is now MessageState from Dapr
            messages.append({"role": msg.role, "content": msg.content})

        # 5. Prepare Tools
        tools = self._get_openai_tools()

        # 6. OpenAI Interaction Loop (Handling Tool Calls)
        # We allow a maximum of 5 turns to prevent infinite loops
        final_response_content = ""
        tool_calls_log = []

        for _ in range(5):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            response_message = response.choices[0].message
            
            # Add the assistant's response to the conversation history for the next turn
            messages.append(response_message)

            if response_message.tool_calls:
                # Handle Tool Calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Inject user_id into arguments
                    arguments["user_id"] = str(user_id)
                    
                    logger.info(f"Executing tool {function_name} with args: {arguments}")
                    
                    try:
                        # Call the tool using FastMCP
                        result = await mcp.call_tool(function_name, arguments)
                        result_str = json.dumps(result, default=str)
                    except Exception as e:
                        logger.error(f"Tool execution failed: {e}")
                        result_str = f"Error: {str(e)}"

                    tool_calls_log.append({
                        "tool": function_name,
                        "args": arguments,
                        "result": result_str
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str
                    })
                # Loop continues to send tool outputs back to OpenAI
            else:
                # No more tool calls, we have the final answer
                final_response_content = response_message.content or ""
                break

        # 7. Persist Assistant Response (T058: Using Dapr State Store)
        if final_response_content:
            await self.conversation_service.add_message(
                conversation_id=current_conversation_id,
                role="assistant",
                content=final_response_content
            )

        return {
            "conversation_id": current_conversation_id,
            "response": final_response_content,
            "tool_calls": tool_calls_log,
            "created_at": datetime.now() # This is approximate, DB has exact time
        }

    def _get_system_prompt(self, user_id: str) -> str:
        try:
            from pathlib import Path
            prompt_path = Path(__file__).parent / "prompts" / "system_prompt.md"
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
            
            return template.replace("{{user_id}}", str(user_id)).replace("{{current_time}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            # Fallback
            return f"You are a helpful Todo Assistant. User ID: {user_id}. Mirror the user's language."

    def _get_openai_tools(self) -> List[ChatCompletionToolParam]:
        mcp_tools = mcp._tool_manager.list_tools()
        openai_tools: List[ChatCompletionToolParam] = []

        for tool in mcp_tools:
            # Deep copy to modify parameters
            tool_def = tool.model_dump()
            parameters = tool_def.get("parameters", {})
            
            # Remove user_id from properties and required
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
