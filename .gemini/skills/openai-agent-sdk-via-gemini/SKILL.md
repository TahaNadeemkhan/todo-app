---
name: openai-agent-sdk-via-gemini
description: Instructions on how to use the OpenAI Agents SDK with a Gemini backend using `OpenAIChatCompletionsModel`. Use this skill when implementing AI agents in Python that need to leverage Gemini's capabilities through the Agents SDK framework.
---

# OpenAI Agents SDK via Gemini

## Instructions
When implementing AI agents using the `openai-agents` Python SDK, you can configure the backend to use Google's Gemini models instead of OpenAI's models. This is done by initializing the `AsyncOpenAI` client with a custom `base_url` pointing to Gemini's OpenAI-compatible endpoint and using your Gemini API key.

**Steps:**
1.  **Install Requirements**: Ensure `openai-agents` and `python-dotenv` are installed.
2.  **Load Environment Variables**: Load the `GEMINI_API_KEY` from the environment.
3.  **Configure AsyncOpenAI**: Create an `AsyncOpenAI` client instance.
    *   Set `api_key` to your Gemini API key.
    *   Set `base_url` to `"https://generativelanguage.googleapis.com/v1beta/openai/"`.
4.  **Configure Model**: Initialize `OpenAIChatCompletionsModel`.
    *   Pass the configured `provider` (the AsyncOpenAI client).
    *   Set the `model` parameter to a valid Gemini model string (e.g., `"gemini-2.0-flash"`).
5.  **Define Tools**: Create your tools using the `@function_tool` decorator.
6.  **Create Agent**: Instantiate the `Agent` class, passing the configured `model` and your tools.
7.  **Run Agent**: Use `Runner` to execute the agent synchronously or asynchronously.