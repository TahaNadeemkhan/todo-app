"use client";

/**
 * Floating Chatbot Widget
 * Bottom-right floating chatbot for dashboard
 *
 * NOTE: ChatKit is a web component that only works in browser.
 * Ensure this component is only rendered client-side.
 */

import { useState, useEffect } from "react";
import { MessageCircle, X, Minimize2 } from "lucide-react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { getChatKitOptions } from "@/lib/chatkit-config";

export function FloatingChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Ensure component only runs in browser
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // ✅ User context automatically extracted from JWT token on backend
  // Note: JWT token automatically sent via cookies by /api/chatkit route
  const { control } = useChatKit(getChatKitOptions());

  // Don't render until mounted in browser
  if (!isMounted) {
    return null;
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center group"
        aria-label="Open chatbot"
      >
        <MessageCircle className="h-6 w-6" />
        <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-500 rounded-full animate-pulse"></span>
      </button>
    );
  }

  return (
    <div
      className={`fixed z-50 bg-white dark:bg-gray-900 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 transition-all ${
        isMinimized
          ? "bottom-6 right-6 w-80 h-16"
          : "bottom-6 right-6 w-96 h-[600px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5" />
          <h3 className="font-semibold">AI Task Assistant</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="hover:bg-blue-800 p-1 rounded transition-colors"
            aria-label={isMinimized ? "Maximize" : "Minimize"}
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-blue-800 p-1 rounded transition-colors"
            aria-label="Close chatbot"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* ChatKit Content */}
      <div
        className={`h-[calc(600px-64px)] overflow-hidden ${isMinimized ? 'hidden' : ''}`}
      >
        <ChatKit
          control={control}
          className="h-full w-full"
          style={{ height: '100%', width: '100%', display: 'block' }}
        />
      </div>
    </div>
  );
}
