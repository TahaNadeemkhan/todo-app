import React, { useState, KeyboardEvent, useEffect } from 'react';
import { MicrophoneButton } from './MicrophoneButton';
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');
  
  const { 
    isListening, 
    startListening, 
    stopListening, 
    browserSupportsSpeech 
  } = useVoiceRecognition((text) => {
    setInput(prev => prev + (prev.length > 0 ? ' ' : '') + text);
  });

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
      if (isListening) stopListening();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center gap-2 p-4 bg-gray-800 border-t border-gray-700">
      {browserSupportsSpeech && (
        <MicrophoneButton 
          isListening={isListening} 
          onStart={startListening} 
          onStop={stopListening}
          disabled={disabled}
        />
      )}
      
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={isListening ? "Listening..." : "Type a message..."}
        disabled={disabled}
        className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      />
      
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-6 py-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <span>Send</span>
      </button>
    </div>
  );
};

