import React from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';

interface MicrophoneButtonProps {
  isListening: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export const MicrophoneButton: React.FC<MicrophoneButtonProps> = ({ 
  isListening, 
  onStart, 
  onStop, 
  disabled 
}) => {
  return (
    <button
      onClick={isListening ? onStop : onStart}
      disabled={disabled}
      className={`relative p-2 rounded-full transition-all duration-200 ${
        isListening 
          ? 'bg-red-500 text-white animate-pulse' 
          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={isListening ? 'Stop listening' : 'Start voice input'}
    >
      {isListening ? (
        <Mic className="w-6 h-6" />
      ) : (
        <MicOff className="w-6 h-6" />
      )}
      
      {isListening && (
        <span className="absolute -top-1 -right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
        </span>
      )}
    </button>
  );
};
