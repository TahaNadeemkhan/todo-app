import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest } from "next/server";

const handler = toNextJsHandler(auth);

export async function GET(request: NextRequest) {
  console.log("[Auth API] GET request:", request.nextUrl.pathname);
  console.log("[Auth API] Origin:", request.headers.get("origin"));
  console.log("[Auth API] Host:", request.headers.get("host"));
  return handler.GET(request);
}

export async function POST(request: NextRequest) {
  console.log("[Auth API] POST request:", request.nextUrl.pathname);
  console.log("[Auth API] Origin:", request.headers.get("origin"));
  console.log("[Auth API] Host:", request.headers.get("host"));
  return handler.POST(request);
}