"use client";

/**
 * Chat Page - OpenAI ChatKit Integration
 * Replaces custom chat components with ChatKit for AI-powered task management
 */

import React from "react";
import { ChatKitPanel } from "@/components/ChatKitPanel";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      <header className="p-4 border-b bg-background">
        <h1 className="text-xl font-bold">AI Task Assistant</h1>
        <p className="text-sm text-muted-foreground">
          Chat with AI to manage your tasks effortlessly
        </p>
      </header>

      <main className="flex-1 overflow-hidden">
        <ChatKitPanel />
      </main>
    </div>
  );
}
