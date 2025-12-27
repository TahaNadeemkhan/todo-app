/**
 * ChatKit API Proxy Route
 * Forwards all ChatKit requests to the backend
 */

import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.text();

    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/chatkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...Object.fromEntries(request.headers.entries()),
      },
      body: body,
    });

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
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error("ChatKit proxy error:", error);
    return Response.json(
      { error: "Failed to connect to ChatKit backend" },
      { status: 500 }
    );
  }
}
