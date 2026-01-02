"use client";

/**
 * Floating Chatbot Widget with Server-Side Voice Processing
 * Records audio -> Sends to Backend -> Gets Text -> Injects into ChatKit
 */

import { useState, memo, useRef, useCallback } from "react";
import { MessageCircle, X, Minimize2, Mic, MicOff } from "lucide-react";
import { ChatKit } from "@openai/chatkit-react";
import { useChatbotContext } from "@/components/ChatbotProvider";
import { toast } from "sonner";

function FloatingChatbotInner() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  // @ts-ignore - sendUserMessage might be missing from type definitions but available at runtime
  const { control, isReady, sendUserMessage } = useChatbotContext();

  // START RECORDING
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      chunksRef.current = [];
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await handleAudioUpload(audioBlob);
        
        // Stop all tracks to release mic
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      // Removed intrusive toast.info('Recording...') - visual pulse is enough

    } catch (err) {
      console.error('Mic access denied:', err);
      toast.error('Could not access microphone');
    }
  };

  // STOP RECORDING
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // SEND TO CHATKIT (Clean Integration)
  const sendToChatKitAPI = async (text: string) => {
      console.log('🎤 Voice input text:', text);

      // Option 1: Try direct method from useChatKit hook
      if (typeof sendUserMessage === 'function') {
          try {
              console.log('Attempting sendUserMessage(text)...');
              // @ts-ignore
              await sendUserMessage(text);
              // Removed toast.success('Message sent!') - redundant as message appears in chat
              return;
          } catch (err) {
              console.warn('sendUserMessage(string) failed, trying object...', err);
              try {
                  // Try object format common in some versions
                  // @ts-ignore
                  await sendUserMessage({ text });
                  return;
              } catch (err2) {
                  console.error('All sendUserMessage attempts failed:', err2);
                  // Fall through to DOM injection
              }
          }
      }
      
      // Option 2: Try method on control object
      if (control && typeof (control as any).sendUserMessage === 'function') {
          try {
             console.log('Attempting control.sendUserMessage(text)...');
             // @ts-ignore
             await (control as any).sendUserMessage(text);
             return;
          } catch (err) {
              console.error('control.sendUserMessage failed:', err);
              // Fall through to DOM injection
          }
      }
      
      // Option 3: Fallback - DOM Injection (Robust)
      console.log('⚠️ Falling back to DOM injection');
      // If we can't programmatically send, we simulate user typing
      // Locate the input area - usually a textarea or input
      const textarea = document.querySelector('textarea[placeholder*="Add"], textarea[placeholder*="Type"], input[type="text"]') as HTMLTextAreaElement | HTMLInputElement;
      
      if (textarea) {
          // React requires dispatching input event to update state
          const nativeValueSetter = Object.getOwnPropertyDescriptor(
              Object.getPrototypeOf(textarea), 
              "value"
          )?.set;
          
          if (nativeValueSetter) {
              nativeValueSetter.call(textarea, text);
          } else {
              textarea.value = text;
          }
          
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
          
          // Wait a tick for state update, then try to find send button
          setTimeout(() => {
              // Look for send button (usually near textarea)
              const sendButton = textarea.closest('div')?.parentElement?.querySelector('button[type="submit"], button[aria-label="Send message"]');
              if (sendButton instanceof HTMLElement) {
                  sendButton.click();
              } else {
                  // Attempt to hit Enter
                  textarea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
              }
          }, 100);
          return;
      }

      console.error("Could not find method to send message or composer element");
      toast.error('Could not send message automatically');
  };

  // SEND TO BACKEND
  const handleAudioUpload = async (audioBlob: Blob) => {
    // Removed toast.loading - visual state should be enough, or add a small spinner if needed
    // But for now, we'll just keep it clean as requested.
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'voice.webm');

      // Call Next.js API route which proxies to FastAPI
      const response = await fetch('/api/voice/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transcription failed');

      const data = await response.json();
      const text = data.text;

      if (text) {
          // Removed toast.success(`Heard: "${text}"`) - redundant
          // Send directly to API instead of injecting into DOM
          sendToChatKitAPI(text);
      } else {
          toast.warning('Could not understand audio');
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to process voice');
    }
  };

  const toggleVoiceInput = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording]);

  if (!isReady) return null;

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
      ref={containerRef}
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
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-blue-800 p-1 rounded transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* ChatKit Content */}
      <div
        className={`relative overflow-hidden ${isMinimized ? 'hidden' : ''}`}
        style={{ height: 'calc(600px - 64px)' }}
      >
        <ChatKit
          key="floating-chatbot-singleton"
          control={control}
          className="h-full w-full"
          style={{ height: '100%', width: '100%', display: 'block' }}
        />

        {/* Floating Mic Button */}
        <button
            onClick={toggleVoiceInput}
            className={`absolute bottom-[20px] right-[60px] z-10 p-2 rounded-full transition-all ${
              isRecording
                ? 'bg-red-500 text-white animate-pulse shadow-lg ring-4 ring-red-500/30'
                : 'bg-transparent text-gray-400 hover:text-blue-600 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
            title={isRecording ? "Stop recording" : "Voice input"}
        >
            {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </button>
      </div>
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const FloatingChatbot = memo(FloatingChatbotInner);
FloatingChatbot.displayName = 'FloatingChatbot';