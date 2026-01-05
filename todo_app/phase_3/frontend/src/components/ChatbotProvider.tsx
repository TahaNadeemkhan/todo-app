"use client";

/**
 * ChatbotProvider
 * Global singleton provider for ChatKit instance
 * Ensures chatbot persists across route changes
 */

import { createContext, useContext, ReactNode, useEffect, useState } from "react";
import { useChatKit } from "@openai/chatkit-react";
import { CHATKIT_OPTIONS } from "@/lib/chatkit-config";

interface ChatbotContextType extends ReturnType<typeof useChatKit> {
  isReady: boolean;
}

const ChatbotContext = createContext<ChatbotContextType | null>(null);

export function ChatbotProvider({ children }: { children: ReactNode }) {
  const [isMounted, setIsMounted] = useState(false);

  // Ensure only runs in browser
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Initialize ChatKit once at app level
  const chatKit = useChatKit(CHATKIT_OPTIONS);

  // Always provide context, but with isReady flag
  return (
    <ChatbotContext.Provider value={{ ...chatKit, isReady: isMounted }}>
      {children}
    </ChatbotContext.Provider>
  );
}

export function useChatbotContext() {
  const context = useContext(ChatbotContext);
  if (!context) {
    throw new Error("useChatbotContext must be used within ChatbotProvider");
  }
  return context;
}
