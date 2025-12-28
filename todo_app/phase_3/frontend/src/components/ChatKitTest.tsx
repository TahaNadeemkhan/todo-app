"use client";

/**
 * MINIMAL ChatKit Test Component
 * Testing if ChatKit initializes at all
 */

import { ChatKit, useChatKit } from "@openai/chatkit-react";

export function ChatKitTest() {
  console.log("ChatKitTest: Component rendering");

  try {
    const chatKit = useChatKit({
      api: {
        url: "/api/chatkit",
        domainKey: "domain_pk_localhost_dev",
      },
    });

    console.log("ChatKitTest: useChatKit hook successful", chatKit);

    return (
      <div className="h-screen w-full bg-gray-100 p-4">
        <h1 className="text-2xl font-bold mb-4">ChatKit Test (Minimal Config)</h1>
        <div className="h-[600px] bg-white border rounded-lg">
          <ChatKit chatKit={chatKit} className="h-full" />
        </div>
      </div>
    );
  } catch (error) {
    console.error("ChatKitTest: Error during initialization", error);
    return (
      <div className="h-screen w-full bg-red-100 p-4">
        <h1 className="text-2xl font-bold text-red-800 mb-4">ChatKit Initialization Error</h1>
        <pre className="bg-white p-4 rounded border text-sm overflow-auto">
          {JSON.stringify(error, null, 2)}
        </pre>
      </div>
    );
  }
}
