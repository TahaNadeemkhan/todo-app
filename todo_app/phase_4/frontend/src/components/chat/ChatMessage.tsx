import React from 'react';
import { Message } from '../../types/chat';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-600 text-white rounded-br-none' 
            : 'bg-gray-700 text-gray-100 rounded-bl-none border border-gray-600'
        }`}
      >
        <div className="prose prose-invert prose-sm">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <div className={`text-xs mt-2 opacity-70 ${isUser ? 'text-blue-100' : 'text-gray-400'}`}>
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};
