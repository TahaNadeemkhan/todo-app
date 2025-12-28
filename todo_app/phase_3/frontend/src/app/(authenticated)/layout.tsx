import { Sidebar } from "@/components/sidebar";
import { FloatingChatbot } from "@/components/FloatingChatbot";
import { ChatbotProvider } from "@/components/ChatbotProvider";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatbotProvider>
      <div className="min-h-screen bg-background flex">
        <Sidebar />

        <main className="flex-1 ml-64 p-8 overflow-auto">
          <div className="max-w-4xl mx-auto">
            {children}
          </div>
        </main>

        {/* Floating AI Chatbot - appears on all authenticated pages */}
        <FloatingChatbot />
      </div>
    </ChatbotProvider>
  );
}
