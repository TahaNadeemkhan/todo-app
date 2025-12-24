import { ChatResponse } from '../types/chat';
import { getSession } from "@/auth"; // Assuming auth setup from Phase 2

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const chatService = {
  async sendMessage(userId: string, message: string, conversationId?: string | null): Promise<ChatResponse> {
    const session = await getSession();
    const token = session?.data?.token; // Adjust based on your Phase 2 auth structure if needed

    // Note: In Phase 3 Hackathon scope, we might not have full Auth middleware on backend active yet 
    // depending on Phase 2 completion, but we'll prepare headers.
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/${userId}/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to send message');
    }

    return response.json();
  }
};
