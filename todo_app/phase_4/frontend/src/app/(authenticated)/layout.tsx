"use client";

import { Sidebar } from "@/components/sidebar";
import { FloatingChatbot } from "@/components/FloatingChatbot";
import { ChatbotProvider } from "@/components/ChatbotProvider";
import { SidebarProvider, useSidebar } from "@/lib/sidebar-context";
import { cn } from "@/lib/utils";

function LayoutContent({ children }: { children: React.ReactNode }) {
  const { isOpen } = useSidebar();

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />

      <div className={cn(
        "flex-1 transition-all duration-300",
        isOpen ? "ml-64" : "ml-20"
      )}>
        <main className="p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Floating AI Chatbot - appears on all authenticated pages */}
      <FloatingChatbot />
    </div>
  );
}

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatbotProvider>
      <SidebarProvider>
        <LayoutContent>{children}</LayoutContent>
      </SidebarProvider>
    </ChatbotProvider>
  );
}
