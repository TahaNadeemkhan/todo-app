"use client";

/**
 * ChatKit Panel Component
 * Integrates OpenAI ChatKit for AI-powered task management chat
 */

import { ChatKit, useChatKit } from "@openai/chatkit-react";
import {
  CHATKIT_API_URL,
  CHATKIT_API_DOMAIN_KEY,
  CHATKIT_THEME,
  CHATKIT_COMPOSER,
  CHATKIT_START_SCREEN,
} from "@/lib/chatkit-config";

export function ChatKitPanel() {
  const chatKit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
    theme: CHATKIT_THEME,
    composer: CHATKIT_COMPOSER,
    startScreen: CHATKIT_START_SCREEN,
  });

  return (
    <div className="h-full w-full">
      <ChatKit chatKit={chatKit} className="h-full" />
    </div>
  );
}
