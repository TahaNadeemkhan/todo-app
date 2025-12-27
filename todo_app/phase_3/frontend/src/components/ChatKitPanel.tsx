"use client";

/**
 * ChatKit Panel Component
 * Integrates OpenAI ChatKit for AI-powered task management chat
 *
 * CORRECT PATTERN FOR @openai/chatkit-react 1.4.0:
 * - useChatKit returns object with { control, ...methods }
 * - ChatKit component expects control={control} prop
 * - domainKey is REQUIRED in api config
 * - All config (theme, composer, startScreen) goes in useChatKit options
 */

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { getChatKitOptions } from "@/lib/chatkit-config";

export function ChatKitPanel() {
  // ✅ User context automatically extracted from JWT token on backend
  // Note: JWT token automatically sent via cookies by /api/chatkit route
  const { control } = useChatKit(getChatKitOptions());

  // CORRECT: Pass control prop to ChatKit component
  return (
    <div className="h-full w-full">
      <ChatKit control={control} className="h-full" />
    </div>
  );
}
