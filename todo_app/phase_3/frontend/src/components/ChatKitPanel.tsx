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
import {
  CHATKIT_API_URL,
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_THEME,
  CHATKIT_COMPOSER,
  CHATKIT_START_SCREEN
} from "@/lib/chatkit-config";

export function ChatKitPanel() {
  // MINIMAL VALID CONFIG - Just API settings
  const { control } = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
  });

  // CORRECT: Pass control prop to ChatKit component
  return (
    <div className="h-full w-full">
      <ChatKit control={control} className="h-full" />
    </div>
  );
}
