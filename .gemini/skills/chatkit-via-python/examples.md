# Examples

## Custom ChatKit Server with FastAPI

```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from openai_chatkit import ChatKitServer, Event, StreamingResult, UserMessageItem, ClientToolCallOutputItem, ThreadMetadata
from openai_chatkit.store import Store, MemoryStore
from openai_chatkit.utils import stream_agent_response, to_input_item
from agents import Agent, Runner, AgentContext
from typing import AsyncIterator, Any

# 1. Implement Server Class
class MyChatKitServer(ChatKitServer):
    def __init__(self, data_store: Store):
        super().__init__(data_store)

    assistant_agent = Agent(
        model="gpt-4.1",
        name="Assistant",
        instructions="You are a helpful assistant",
    )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallOutputItem,
        context: Any,
    ) -> AsyncIterator[Event]:
        # Create context with store and request-specific data
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )
        
        # Run agent streaming
        result = Runner.run_streamed(
            self.assistant_agent,
            await to_input_item(input, self.to_message_content),
            context=agent_context,
        )
        
        # Stream events back to client
        async for event in stream_agent_response(agent_context, result):
            yield event

    async def to_message_content(self, input):
        # Implement file handling logic here if needed
        raise NotImplementedError()

# 2. Setup App & Endpoint
app = FastAPI()
data_store = MemoryStore() # Use SQLiteStore or custom Store for persistence
server = MyChatKitServer(data_store)

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Pass request body and optional context (e.g., auth user)
    result = await server.process(await request.body(), {})
    
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

## Client Tool Triggering

```python
from agents import function_tool, ClientToolCall, StopAtTools

@function_tool(description_override="Add an item to the user's todo list.")
async def add_to_todo_list(ctx, item: str) -> None:
    # Trigger a client-side tool execution
    ctx.context.client_tool_call = ClientToolCall(
        name="add_to_todo_list",
        arguments={"item": item},
    )

# Agent configuration to stop at this tool
assistant_agent = Agent(
    model="gpt-4.1",
    name="Assistant",
    tools=[add_to_todo_list],
    tool_use_behavior=StopAtTools(stop_at_tool_names=[add_to_todo_list.name]),
)
```
