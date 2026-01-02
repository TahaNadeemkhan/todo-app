from enum import Enum
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

print(f"str(MessageRole.USER): {str(MessageRole.USER)}")
print(f"MessageRole.USER.value: {MessageRole.USER.value}")
print(f"MessageRole.USER.name: {MessageRole.USER.name}")
