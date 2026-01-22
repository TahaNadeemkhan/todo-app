# Voice Refactor Plan: Client-Side Audio -> Server-Side STT

## Context
The user wants to move away from the fragile browser-based Web Speech API (which requires finding and injecting into inputs) to a robust server-side solution.
The frontend will record audio and send it to the backend. The backend will transcribe it (using Google Cloud STT or OpenAI Whisper or similar) and then feed it into the ChatKit system.

## Stack
- **Frontend:** React (Next.js) + MediaRecorder API
- **Backend:** FastAPI (Python)
- **STT Service:** Google Cloud Speech-to-Text (preferred by user context "google ka stt") or OpenAI Whisper (since we have OpenAI deps).
    - *Decision:* User said "google ka stt", so we will aim for Google Cloud Speech-to-Text. However, if credentials aren't available, we might fallback or ask. For now, we'll assume Google.

## Implementation Steps

### Phase 1: Backend Setup
1.  **Dependencies:** Add `google-cloud-speech` (or `speechrecognition` for lighter wrapper) to `requirements.txt`.
2.  **Endpoint:** Create `POST /api/voice/transcribe`.
    -   Input: `UploadFile` (audio blob, likely `webm` or `wav`).
    -   Logic:
        1.  Save temp file.
        2.  Call Google STT API.
        3.  Return JSON: `{ "text": "transcribed text" }`.
    -   *Alternative Flow:* The user said "backend... text main convert karny k baad... chatkit end point ko dedega".
        -   This implies the backend should *directly* invoke ChatKit logic with the text, effectively acting as "User sent a message".
        -   However, ChatKit is a request-response protocol usually initiated by the client.
        -   *Better approach:* The backend returns the text to the frontend, and the *frontend* sends it to ChatKit (via `control.send(text)` or similar). This keeps the ChatKit protocol clean.
        -   *Even better:* The frontend sends audio -> Backend transcribes -> Backend returns text -> Frontend puts text in input box (or auto-sends).
        -   *Wait*, the user said "direct origional search bar mai hi rkho" previously, but now says "backend k pas jana chiye... wo text main convert karny k baad... chatkit end point ko dedega".
        -   This strongly suggests a "Voice Message" flow where the user speaks, and it appears as a message.

### Phase 2: Frontend Refactor (`FloatingChatbot.tsx`)
1.  **Remove:** `webkitSpeechRecognition` logic.
2.  **Add:** `MediaRecorder` logic.
    -   State: `isRecording`.
    -   UI: Mic button press -> `recorder.start()`. Release/Click again -> `recorder.stop()`.
    -   Event: `ondataavailable` -> collect chunks.
    -   Event: `onstop` -> Create `Blob` -> `FormData` -> `fetch('/api/voice/transcribe')`.
3.  **Handle Response:**
    -   Receive text.
    -   *Option A (Auto-send):* Use ChatKit `control` to send the message? `useChatKit` might expose `send`.
    -   *Option B (Inject):* Put it in the input box. User prefers "direct... chatkit end point ko dedega".
    -   We will try to have the backend return the text, and the frontend will utilize `ChatKit` context methods to submit it, OR the backend can create the thread message directly (but that complicates the real-time UI update).
    -   *Safest path:* Backend returns text, frontend injects it into the *visible* ChatKit instance (using the robust injection we just built, or better, a cleaner `control` method if available).

## User Confirmation Needed
-   Do we have Google Cloud Credentials (`GOOGLE_APPLICATION_CREDENTIALS`)?
-   Or should we use OpenAI Whisper (since we have `openai` pkg)?
    -   *Assumption:* User said "google ka stt". I'll start with that but need to verify auth.

## Revised Plan for User
I will propose:
1.  **Frontend:** Record audio -> Send to Backend.
2.  **Backend:** Transcribe Audio -> Return Text.
3.  **Frontend:** Receive Text -> Auto-send to ChatKit.

This is robust and keeps the "user sees their message" UX.
