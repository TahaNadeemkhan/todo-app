---
name: chatkit-via-python
description: Instructions on how to build a custom, self-hosted ChatKit server using Python and FastAPI. Use this skill when you need advanced customization, custom authentication, or on-prem deployment of OpenAI's ChatKit interface.
---

# Advanced ChatKit via Python

## Instructions
To run ChatKit on your own infrastructure, you need to implement a custom `ChatKitServer` that handles requests, executes tools via the OpenAI Agents SDK, and streams events back to the client.

### 1. Requirements
*   Install the server package: `pip install openai-chatkit`
*   Install OpenAI Agents SDK: `pip install openai-agents`
*   Use a Python web framework (e.g., FastAPI) to expose the endpoint.

### 2. Implementation Steps
1.  **Server Class**: Create a class inheriting from `ChatKitServer`.
2.  **Overrides**: Override the `respond` method to handle user input.
3.  **Agents Integration**: Use `Runner.run_streamed` to execute an agent and `stream_agent_response` to yield events to the client.
4.  **Data Persistence**: Implement `chatkit.store.Store` (e.g., SQLite, Postgres) to persist threads and messages.
5.  **Expose Endpoint**: Create a POST endpoint (e.g., `/chatkit`) that delegates to `server.process(request.body)`.

### 3. Key Concepts
*   **Widgets**: Use `stream_widget` to render interactive UI elements (cards, forms) directly from the server.
*   **Client Tools**: Use `ctx.context.client_tool_call` to trigger actions on the frontend (e.g., opening a modal).
*   **Actions**: Handle UI interactions (button clicks) via the `action` method on your server class.
*   **File Store**: Implement `FileStore` if you need to support file uploads.

### 4. Integration Pattern
*   **Frontend**: Use the ChatKit Web Component or client SDK, pointing `apiURL` to your FastAPI endpoint.
*   **Authentication**: Pass custom context (e.g., user ID) to `server.process` to enforce permissions.