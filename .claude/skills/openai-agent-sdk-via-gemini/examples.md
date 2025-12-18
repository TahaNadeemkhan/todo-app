# Examples

## Basic Implementation with Function Tool

```python
from unittest import result
from agents import Agent, Runner, AsyncOpenAI, function_tool, set_tracing_disabled, OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure AsyncOpenAI for Gemini
provider = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. Configure the Model
model = OpenAIChatCompletionsModel(
    openai_client=provider,
    model="gemini-2.0-flash",
)

# 4. Define Tools
@function_tool
def calculate_fabonacci(n: int) -> int:
    '''adds the fabonacci of a number'''
    # Note: This is a sample implementation logic
    return f"Fabonacci: {n - 1} + {n - 2}"

# 5. Create the Agent
agent = Agent(
    name="Fabonacci Assistant",
    instructions="You are a helping assistant, you only reply with fabonacci series",
    tools=[calculate_fabonacci],
    model=model
)

# 6. Run the Agent
# Ensure tracing is handled if needed
# set_tracing_disabled(True) 

result = Runner.run_sync(agent, input="what is fabonacci of 5")
print(result.final_output)
```
