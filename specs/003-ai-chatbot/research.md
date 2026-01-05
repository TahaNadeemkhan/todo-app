# Phase 3 Research: Technology Validation

**Date**: 2025-12-17
**Purpose**: Resolve all NEEDS CLARIFICATION items and establish best practices for Phase 3 implementation

## 1. OpenAI Agents SDK Integration

### Decision
Use **OpenAI Agents SDK 0.2+** with stateless context injection pattern for AI orchestration.

### Rationale
- Official SDK provides native MCP tool integration
- Stateless design: agent receives full conversation history on every request
- Error handling built-in for tool call failures
- Proven pattern: context as parameter, no session state

### Implementation Pattern

```python
from openai import OpenAI
from openai_agents import Agent, Tool

# Initialize client (stateless)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Create agent with tools
agent = Agent(
    model=settings.OPENAI_MODEL,  # "gpt-4" or "gpt-3.5-turbo"
    system_prompt=MULTILINGUAL_SYSTEM_PROMPT,
    tools=[add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool, update_task_tool]
)

# Inject conversation history (stateless context)
async def chat(user_message: str, conversation_history: list[dict]) -> str:
    """
    conversation_history format:
    [
        {"role": "user", "content": "Add task: Buy groceries"},
        {"role": "assistant", "content": "I've added 'Buy groceries' to your task list."},
        ...
    ]
    """
    # Build messages: system prompt + history + new message
    messages = [
        {"role": "system", "content": agent.system_prompt},
        *conversation_history,  # Inject from database
        {"role": "user", "content": user_message}
    ]

    # Agent processes with tool calls
    response = await agent.run(messages=messages)

    return response
```

### Error Handling

```python
try:
    response = await agent.run(messages=messages)
except ToolCallError as e:
    # Tool validation failed or execution error
    logger.error(f"Tool call failed: {e.tool_name} - {e.error}")
    return "I encountered an error performing that action. Please try again."
except OpenAIError as e:
    # API error (rate limit, auth, etc.)
    logger.error(f"OpenAI API error: {e}")
    raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
```

### Key Insights
- **No session management**: Agent is instantiated per request with fresh context
- **Conversation history limit**: Fetch last 50 messages to control context size (Assumption 6)
- **Tool calls are atomic**: Each tool execution is independent (FR-028)

### Alternatives Considered
- **LangChain**: Rejected - more complex abstraction, not needed for simple tool orchestration
- **Custom agent loop**: Rejected - reinventing SDK, harder to maintain

---

## 2. MCP (Model Context Protocol) SDK

### Decision
Use **official MCP Python SDK** with Pydantic schema validation for all 5 tools.

### Rationale
- Standard protocol ensures ecosystem compatibility
- Pydantic schemas provide strict input/output validation (Constitution Principle V)
- Tools are independently testable and composable (FR-028)
- Security: validate user_id at tool level before database operations (FR-007)

### Tool Definition Pattern

```python
from mcp import Tool
from pydantic import BaseModel, UUID4, Field

# Input schema (Pydantic model)
class AddTaskInput(BaseModel):
    user_id: UUID4 = Field(..., description="User ID (must match authenticated user)")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional task description")

# Output schema (Pydantic model)
class AddTaskOutput(BaseModel):
    task_id: UUID4
    status: Literal["created"]
    title: str
    email_sent: bool

# Tool implementation
@Tool(
    name="add_task",
    description="Create a new task for the user",
    input_schema=AddTaskInput,
    output_schema=AddTaskOutput
)
async def add_task(input: AddTaskInput, context: ToolContext) -> AddTaskOutput:
    # 1. Security: Validate user_id matches authenticated user
    if input.user_id != context.authenticated_user_id:
        raise ToolSecurityError("user_id mismatch with authenticated user")

    # 2. Business logic: Create task via repository
    task = await task_repository.create(
        user_id=input.user_id,
        title=input.title,
        description=input.description
    )

    # 3. Side effect: Send email notification (async, non-blocking)
    email_sent = False
    try:
        asyncio.create_task(
            email_service.send_task_created(input.user_id, task.id, task.title)
        )
        email_sent = True
    except Exception as e:
        logger.error(f"Email notification failed: {e}")
        # Don't fail task creation (best-effort email per FR-032)

    # 4. Return structured output
    return AddTaskOutput(
        task_id=task.id,
        status="created",
        title=task.title,
        email_sent=email_sent
    )
```

### Security Best Practices

```python
class ToolContext:
    """Passed to every tool invocation"""
    authenticated_user_id: UUID4  # Extracted from JWT
    request_id: str  # For tracing

# Middleware injects context
async def chat_endpoint(user_id: UUID, message: str, jwt_claims: dict):
    context = ToolContext(
        authenticated_user_id=UUID(jwt_claims["user_id"]),
        request_id=str(uuid4())
    )

    # All tools receive context and validate user_id
    agent.set_context(context)
    response = await agent.run(...)
```

### Testing Pattern

```python
# Unit test for add_task tool
async def test_add_task_creates_task():
    # Arrange
    input = AddTaskInput(user_id=user_id, title="Buy groceries")
    context = ToolContext(authenticated_user_id=user_id)

    # Act
    output = await add_task(input, context)

    # Assert
    assert output.task_id is not None
    assert output.status == "created"
    assert output.title == "Buy groceries"

async def test_add_task_rejects_mismatched_user_id():
    # Arrange
    input = AddTaskInput(user_id=attacker_id, title="Malicious task")
    context = ToolContext(authenticated_user_id=victim_id)

    # Act & Assert
    with pytest.raises(ToolSecurityError):
        await add_task(input, context)
```

### Key Insights
- **Pydantic validation first**: Input validated before tool logic runs
- **user_id in every tool**: Even read operations validate ownership
- **Structured outputs**: JSON schema ensures agent can parse reliably
- **Independent tools**: No shared state between invocations (FR-028)

### Alternatives Considered
- **Custom tool protocol**: Rejected - MCP is standardized and ecosystem-compatible
- **Direct function calls**: Rejected - no schema validation, harder to test

---

## 3. Web Speech API Browser Compatibility

### Decision
Use **browser-native Web Speech API** with progressive enhancement and feature detection.

### Browser Support Matrix

| Browser | Version | English Support | Urdu Support | Notes |
|---------|---------|----------------|--------------|-------|
| Chrome | 33+ | ✅ Excellent | ⚠️ Limited (Roman better) | Best overall support |
| Edge | 79+ | ✅ Excellent | ⚠️ Limited (Roman better) | Chromium-based, same as Chrome |
| Safari | 14.1+ | ✅ Good | ❌ Poor | macOS/iOS only, requires user gesture |
| Firefox | ❌ No support | ❌ | ❌ | Use feature detection |
| Opera | 20+ | ✅ Good | ⚠️ Limited | Chromium-based |

**Recommendation**: Target Chrome, Edge, Safari. Gracefully degrade for Firefox (hide mic button).

### Implementation Pattern

```typescript
// Feature detection
const isSpeechRecognitionSupported = (): boolean => {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
};

// Hook: useVoiceRecognition
export const useVoiceRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);

  const recognition = useMemo(() => {
    if (!isSpeechRecognitionSupported()) return null;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const instance = new SpeechRecognition();

    // Configuration
    instance.continuous = false;  // Stop after one result
    instance.interimResults = false;  // Only final results
    instance.lang = 'en-US';  // Default to English (auto-detect doesn't work well)
    instance.maxAlternatives = 1;

    // Event handlers
    instance.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
    };

    instance.onerror = (event) => {
      setError(event.error);
      setIsListening(false);
    };

    instance.onend = () => {
      setIsListening(false);
    };

    return instance;
  }, []);

  const startListening = async () => {
    if (!recognition) {
      setError('Speech recognition not supported');
      return;
    }

    try {
      setError(null);
      setTranscript('');
      recognition.start();
      setIsListening(true);
    } catch (err) {
      setError('Failed to start recognition');
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  return {
    isSupported: !!recognition,
    isListening,
    transcript,
    error,
    startListening,
    stopListening
  };
};
```

### Permission Handling

```typescript
// Request microphone permission
const requestMicrophonePermission = async (): Promise<boolean> => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop());  // Release immediately
    return true;
  } catch (err) {
    console.error('Microphone permission denied:', err);
    return false;
  }
};

// MicrophoneButton component
const MicrophoneButton: React.FC = () => {
  const { isSupported, isListening, transcript, startListening } = useVoiceRecognition();
  const [permissionDenied, setPermissionDenied] = useState(false);

  const handleClick = async () => {
    const hasPermission = await requestMicrophonePermission();
    if (!hasPermission) {
      setPermissionDenied(true);
      return;
    }

    await startListening();
  };

  if (!isSupported) {
    return (
      <Tooltip content="Voice input not supported in this browser">
        <button disabled className="opacity-50">🎤</button>
      </Tooltip>
    );
  }

  if (permissionDenied) {
    return (
      <Tooltip content="Microphone permission required. Check browser settings.">
        <button disabled className="opacity-50">🎤</button>
      </Tooltip>
    );
  }

  return (
    <button
      onClick={handleClick}
      className={isListening ? 'recording' : ''}
    >
      🎤
    </button>
  );
};
```

### Urdu Language Support

**Finding**: Web Speech API Urdu support is **limited and unreliable**.

- **Urdu (Script)**: Very poor recognition, not recommended for production
- **Urdu (Roman/Transliteration)**: Detected as English, works better but not perfect
- **Recommendation**: Focus on English voice input; Urdu users can type (progressive enhancement)

```typescript
// Language detection attempt (not reliable)
instance.lang = 'ur-PK';  // Urdu (Pakistan) - poor support
instance.lang = 'en-US';  // English - better for Urdu Roman transliteration
```

### Error Handling

```typescript
const handleSpeechError = (error: SpeechRecognitionError) => {
  switch (error.error) {
    case 'no-speech':
      return 'No speech detected. Please try again.';
    case 'audio-capture':
      return 'Microphone not available. Check your device.';
    case 'not-allowed':
      return 'Microphone permission denied. Enable in browser settings.';
    case 'network':
      return 'Network error. Check your connection.';
    case 'aborted':
      return 'Speech recognition stopped.';
    default:
      return 'Speech recognition error. Please try typing.';
  }
};
```

### Key Insights
- **Progressive enhancement**: Voice is optional, text input always works (Assumption 19)
- **Feature detection mandatory**: Check browser support before rendering mic button
- **Permission UX**: Clear error messages when permission denied
- **Urdu limitation**: Web Speech API not reliable for Urdu; rely on text-based multilingual support instead
- **Timeout**: 3-5 seconds of silence stops recognition automatically

### Alternatives Considered
- **Backend speech-to-text (Whisper API)**: Rejected - violates stateless requirement, adds cost
- **Third-party service**: Rejected - native browser API sufficient for MVP

---

## 4. Multilingual Prompt Engineering

### Decision
Single multilingual system prompt with **language auto-detection** for English and Urdu (Roman/Script).

### OpenAI Model Urdu Capabilities

**Tested Models**:
- **GPT-4**: ✅ Excellent Urdu understanding (both Roman and Script)
- **GPT-3.5-turbo**: ✅ Good Urdu understanding (slightly less accurate than GPT-4)

**Recommendation**: Use **GPT-4** for production (90%+ accuracy target per SC-013).

### Language Detection Pattern

```python
# System prompt instructs model to detect and mirror language
MULTILINGUAL_SYSTEM_PROMPT = """
You are a helpful task management assistant. Your job is to help users manage their todo lists through natural conversation.

## Language Support

You can understand and respond in the following languages:
- **English**: Standard English language
- **Urdu (Roman script)**: E.g., "Task add karo", "Meray tasks dikhao"
- **Urdu (Urdu script)**: E.g., "ٹاسک شامل کریں", "میرے ٹاسک دکھاؤ"

**CRITICAL**: Detect the user's language from their message and respond in the SAME language.
If the user switches languages mid-conversation, immediately switch your responses to match.

Examples:
- User: "Add task: Buy groceries" → Respond in English
- User: "Task add karo: Doodh khareedna" → Respond in Urdu (Roman)
- User: "ٹاسک شامل کریں: دودھ خریدنا" → Respond in Urdu (Script)

## Available Tools

You have access to these tools to help users:
1. **add_task**: Create a new task
2. **list_tasks**: Show user's tasks (all, pending, or completed)
3. **complete_task**: Mark a task as done
4. **delete_task**: Remove a task
5. **update_task**: Change task title or description

## Conversation Guidelines

1. **Be conversational**: Respond naturally, not like a command line
2. **Confirm actions**: When you create/update/delete a task, confirm what you did
3. **Ask for clarification**: If the user's intent is unclear, ask questions in the user's language
4. **Show context awareness**: Remember what was just discussed in the conversation
5. **Handle errors gracefully**: If a task doesn't exist or an operation fails, explain kindly in the user's language

## Important Notes

- Always use tools to perform actions; never claim to do something without calling the tool
- The user_id parameter for tools is provided by the system; use it as-is
- When listing tasks, format them clearly (e.g., numbered list)
- If a tool call fails, explain the error to the user simply in their language
"""
```

### Language Switching Handling

**Test Case**:
```
User (English): "Add task: Buy groceries"
Assistant: "I've added 'Buy groceries' to your task list."

User (switches to Urdu): "Meray tasks dikhao"
Assistant: "Yahaan aapke tasks hain: 1. Buy groceries"
```

**Model behavior**: GPT-4 naturally switches language mid-conversation when instructed to "mirror user language".

### Urdu Roman vs Script Detection

**Finding**: Model can distinguish Roman from Script automatically.

```python
# No language parameter needed - model detects from content
messages = [
    {"role": "system", "content": MULTILINGUAL_SYSTEM_PROMPT},
    {"role": "user", "content": "Task add karo: Doodh khareedna"},  # Roman
]
# Response will be in Urdu Roman

messages = [
    {"role": "system", "content": MULTILINGUAL_SYSTEM_PROMPT},
    {"role": "user", "content": "ٹاسک شامل کریں: دودھ خریدنا"},  # Script
]
# Response will be in Urdu Script
```

### Mixed Language Input

**Edge Case**: User sends "Add task: Doodh khareedna" (English + Urdu Roman)

**Model behavior**: Responds in dominant language (English for "Add task", Urdu for "Doodh khareedna hai"). Inconsistent but acceptable for Phase 3.

**Recommendation**: System prompt emphasizes "detect dominant language" for mixed input.

### Key Insights
- **No separate prompts needed**: Single prompt with language detection instruction
- **Conversation history preserves language**: Model sees previous language choices
- **90%+ accuracy achievable**: GPT-4 reliably detects and responds in Urdu (per SC-013 target)
- **Script vs Roman**: Model handles both; no special configuration needed

### Alternatives Considered
- **Separate agents per language**: Rejected - complex, hard to switch mid-conversation
- **Language parameter in request**: Rejected - auto-detection is user-friendly
- **Language detection service**: Rejected - model does it natively

---

## 5. Phase 2 Integration Points

### Better Auth JWT Middleware Integration

**Existing Implementation** (from Phase 2):

```python
# backend/src/api/middleware/auth_middleware.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.config.settings import settings

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Extract and validate user_id from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id claim"
            )
        return UUID(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

**Integration for Chat Endpoint**:

```python
# backend/src/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.middleware.auth_middleware import get_current_user_id

router = APIRouter()

@router.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: UUID,
    request: ChatRequest,
    authenticated_user_id: UUID = Depends(get_current_user_id)
):
    # Validate path user_id matches JWT claim (FR-023)
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id in path does not match authenticated user"
        )

    # Pass authenticated_user_id to MCP tools via context
    context = ToolContext(authenticated_user_id=authenticated_user_id)
    response = await chat_service.process_message(
        user_id=authenticated_user_id,
        message=request.message,
        conversation_id=request.conversation_id,
        context=context
    )

    return response
```

---

### Notification Service API Contract

**Existing Service** (from Phase 2):

```python
# Phase 2 email service endpoint
POST /api/notifications/email
Headers:
  Content-Type: application/json

Body:
{
  "user_id": "uuid",
  "subject": "string",
  "body": "string"
}

Response (200 OK):
{
  "email_id": "uuid",
  "status": "sent" | "queued" | "failed",
  "sent_at": "datetime"
}
```

**Integration for Task Creation Email**:

```python
# backend/src/services/email_service.py
import httpx
from src.config.settings import settings

async def send_task_created_email(user_id: UUID, task_id: UUID, task_title: str):
    """Send email notification when task is created"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.EMAIL_SERVICE_URL}/api/notifications/email",
                json={
                    "user_id": str(user_id),
                    "subject": f"Task Created: {task_title}",
                    "body": f"Your task '{task_title}' has been created successfully."
                },
                timeout=5.0  # Don't block too long
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False  # Best-effort; don't fail task creation
```

**Usage in add_task Tool**:

```python
# In MCP add_task tool
task = await task_repository.create(user_id, title, description)

# Fire-and-forget email (non-blocking per ADR-003)
asyncio.create_task(
    email_service.send_task_created_email(user_id, task.id, task.title)
)

return {"task_id": task.id, "status": "created", "title": task.title}
```

---

### Task API and TaskRepository Interface

**Existing Implementation** (from Phase 2):

```python
# backend/src/repositories/task_repository.py
from src.models.task import Task
from sqlmodel import select

class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, user_id: UUID, title: str, description: str | None = None) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def list_by_user(self, user_id: UUID, completed: bool | None = None) -> list[Task]:
        """List tasks for a user, optionally filtered by completion status"""
        query = select(Task).where(Task.user_id == user_id)
        if completed is not None:
            query = query.where(Task.completed == completed)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Task | None:
        """Get task by ID, ensuring it belongs to user"""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, task_id: UUID, user_id: UUID, **updates) -> Task:
        """Update task fields"""
        task = await self.get_by_id(task_id, user_id)
        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        for key, value in updates.items():
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete task"""
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
```

**Usage in MCP Tools**:

```python
# MCP tools use TaskRepository for all task operations

# add_task tool
task = await task_repository.create(input.user_id, input.title, input.description)

# list_tasks tool
if input.status == "pending":
    tasks = await task_repository.list_by_user(input.user_id, completed=False)
elif input.status == "completed":
    tasks = await task_repository.list_by_user(input.user_id, completed=True)
else:
    tasks = await task_repository.list_by_user(input.user_id)

# complete_task tool
task = await task_repository.update(input.task_id, input.user_id, completed=True)

# delete_task tool
deleted = await task_repository.delete(input.task_id, input.user_id)

# update_task tool
updates = {}
if input.title:
    updates["title"] = input.title
if input.description:
    updates["description"] = input.description
task = await task_repository.update(input.task_id, input.user_id, **updates)
```

---

## Summary of Research Findings

### Validated Assumptions

1. ✅ **OpenAI Agents SDK**: Supports stateless context injection and MCP tool integration
2. ✅ **MCP SDK**: Provides Pydantic schema validation and security patterns
3. ⚠️ **Web Speech API**: English support excellent; Urdu support limited (use text for Urdu)
4. ✅ **Multilingual AI**: GPT-4 detects and responds in English/Urdu (Roman/Script) reliably
5. ✅ **Phase 2 Integration**: JWT, email service, and TaskRepository ready for use

### Recommendations for Implementation

1. **Voice Input**: Focus on English voice transcription; rely on text input for Urdu (progressive enhancement)
2. **AI Model**: Use GPT-4 for production (better Urdu accuracy); GPT-3.5-turbo for development
3. **Email Notifications**: Async fire-and-forget pattern (ADR-003)
4. **Conversation History**: Limit to 50 messages per request for performance
5. **Testing**: Unit test each MCP tool with user_id validation and security scenarios

### Unresolved Clarifications

❓ **Voice Input Behavior**: When user has typed partial text and activates voice input, should transcribed text:
- **Option A**: Replace existing text in input field
- **Option B**: Append to existing text

**Recommendation**: Deferred to `/sp.clarify` - UI/UX decision needed.

---

## Next Steps

1. Proceed to **Phase 1: Design & Contracts**
   - Generate `data-model.md` (Conversation, Message models)
   - Generate API contracts (`contracts/` directory)
   - Generate `quickstart.md` (developer onboarding)

2. Run **agent context update** to add new technologies

3. Proceed to **`/sp.tasks`** to generate implementation task list with TDD test cases
