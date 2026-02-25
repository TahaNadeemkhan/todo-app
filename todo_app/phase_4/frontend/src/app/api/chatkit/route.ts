/**
 * ChatKit API Proxy Route
 * Forwards all ChatKit requests to the backend
 * ✅ Adds Better Auth session user_id directly in request
 */

import { NextRequest } from "next/server";
import { auth } from "@/lib/auth"; // Better Auth server instance

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

export async function GET(request: NextRequest) {
  console.log("🔍 ChatKit GET request received");
  return Response.json({ status: "ChatKit API route is working", backend: BACKEND_URL });
}

export async function POST(request: NextRequest) {
  console.log("🚀 ChatKit API route called");

  try {
    // Get the request body
    const body = await request.text();
    console.log("📦 Request body received, length:", body.length);

    // ✅ CRITICAL: Get session using Better Auth server-side
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    console.log("👤 Session from Better Auth:", session ? `✅ User: ${session.user?.id}` : "❌ Not authenticated");

    // ✅ CRITICAL: Add user context to request body
    let requestData = JSON.parse(body);

    // Inject user_id into the request if session exists
    if (session?.user?.id) {
      // Add user_id to context field for ChatKit
      requestData.context = session.user.id;
      console.log(`🔑 Injected user_id into context: ${session.user.id}`);
    } else {
      console.warn("⚠️ No session found, request will use backend fallback");
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Forward the request to the backend with modified body
    const modifiedBody = JSON.stringify(requestData);
    console.log(`📡 Forwarding to backend: ${BACKEND_URL}/chatkit`);
    console.log(`📦 Modified body context:`, requestData.context || 'none');

    const response = await fetch(`${BACKEND_URL}/chatkit`, {
      method: "POST",
      headers,
      body: modifiedBody,
    });
    console.log("✅ Backend responded with status:", response.status);

    // Check if it's a streaming response
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("text/event-stream")) {
      // Return streaming response
      return new Response(response.body, {
        status: response.status,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // Return regular JSON response
    const data = await response.json();
    console.log("📤 Sending JSON response to frontend");
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error("❌ ChatKit proxy error:", error);
    console.error("Error details:", error instanceof Error ? error.message : String(error));
    return Response.json(
      { error: "Failed to connect to ChatKit backend", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
