import { useState, useCallback } from 'react';
import { chatService } from '../services/chatService';
import { Message, ChatState } from '../types/chat';

export const useChatConversation = (userId: string) => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    conversationId: null,
    isLoading: false,
    error: null,
  });

  const sendMessage = useCallback(async (content: string) => {
    setState((prev) => ({ 
      ...prev, 
      isLoading: true, 
      error: null,
      // Optimistically add user message
      messages: [
        ...prev.messages, 
        { 
          id: `temp-${Date.now()}`, 
          role: 'user', 
          content, 
          created_at: new Date().toISOString() 
        }
      ]
    }));

    try {
      const response = await chatService.sendMessage(userId, content, state.conversationId);
      
      setState((prev) => ({
        ...prev,
        isLoading: false,
        conversationId: response.conversation_id,
        messages: [
          ...prev.messages,
          {
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: response.response,
            created_at: response.created_at
          }
        ]
      }));
    } catch (err: any) {
      setState((prev) => ({ 
        ...prev, 
        isLoading: false, 
        error: err.message || 'Failed to send message' 
      }));
    }
  }, [userId, state.conversationId]);

  return {
    ...state,
    sendMessage
  };
};
