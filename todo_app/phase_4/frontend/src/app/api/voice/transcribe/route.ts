/**
 * Voice Transcription API Proxy Route
 * Forwards audio files to the backend for transcription
 * Supports: OpenAI Whisper or Gemini 1.5 Flash (backend decides)
 */

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

export async function POST(request: NextRequest) {
  console.log("🎤 Voice transcribe API route called");

  try {
    // Get the form data with audio file
    const formData = await request.formData();
    const audioFile = formData.get("file");

    if (!audioFile) {
      console.error("❌ No audio file in request");
      return NextResponse.json(
        { error: "No audio file provided" },
        { status: 400 }
      );
    }

    console.log("📦 Audio file received, forwarding to backend...");

    // Forward to backend
    const backendFormData = new FormData();
    backendFormData.append("file", audioFile);

    const response = await fetch(`${BACKEND_URL}/voice/transcribe`, {
      method: "POST",
      body: backendFormData,
    });

    console.log("✅ Backend responded with status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Backend error:", errorText);
      return NextResponse.json(
        { error: "Transcription failed", details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log("📤 Transcription result:", data);

    return NextResponse.json(data);
  } catch (error) {
    console.error("❌ Voice transcribe proxy error:", error);
    return NextResponse.json(
      {
        error: "Failed to transcribe audio",
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}
