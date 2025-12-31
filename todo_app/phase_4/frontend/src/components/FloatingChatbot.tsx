"use client";

/**
 * Floating Chatbot Widget with Voice Input
 * Uses Web Speech API for voice-to-text, then sends to ChatKit
 */

import { useState, memo, useEffect, useRef, useCallback } from "react";
import { MessageCircle, X, Minimize2, Mic, MicOff } from "lucide-react";
import { ChatKit } from "@openai/chatkit-react";
import { useChatbotContext } from "@/components/ChatbotProvider";
import { toast } from "sonner";

function FloatingChatbotInner() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState<string>("");
  const recognitionRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const { control, isReady } = useChatbotContext();

  // Initialize Web Speech API
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('Web Speech API not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    // Cached reference to the input element
    let cachedInput: HTMLElement | null = null;

    const findInput = (): HTMLElement | null => {
        if (cachedInput && document.contains(cachedInput)) return cachedInput;

        // Base selectors - removed placeholder constraint for container search
        const broadSelectors = 'textarea, input[type="text"], [contenteditable="true"]';

        // Helper: Recursive search that handles Shadow DOM AND Iframes
        const recursiveSearch = (root: ParentNode | Document): Element | null => {
            // 1. Check direct match in current root
            // Prioritize visible elements
            const candidates = Array.from(root.querySelectorAll(broadSelectors));
            const visible = candidates.find(el => {
                 const style = window.getComputedStyle(el);
                 return style.display !== 'none' && style.visibility !== 'hidden';
            });
            if (visible) return visible;

            // 2. Traverse children for Shadow Roots and Iframes
            const allElements = root.querySelectorAll('*');
            for (const el of Array.from(allElements)) {
                // Check Shadow DOM
                if (el.shadowRoot) {
                    const found = recursiveSearch(el.shadowRoot);
                    if (found) return found;
                }
                // Check Iframe (if same origin)
                if (el.tagName === 'IFRAME') {
                    try {
                        const iframeDoc = (el as HTMLIFrameElement).contentDocument;
                        if (iframeDoc) {
                            const found = recursiveSearch(iframeDoc);
                            if (found) return found;
                        }
                    } catch (e) {
                        // Cross-origin iframe access blocked
                        console.warn('⚠️ [Voice] Cannot access iframe content:', e);
                    }
                }
            }
            return null;
        };

        // 1. Preferred: Search inside our container (Broad search)
        if (containerRef.current) {
            console.log('🔍 [Voice] Searching container (Broad)...');
            const found = recursiveSearch(containerRef.current);
            if (found) {
                console.log('✅ [Voice] Found input in container:', found);
                cachedInput = found as HTMLElement;
                return cachedInput;
            }
        }

        // 2. Active Element Strategy (If user clicked it)
        if (document.activeElement && 
            (document.activeElement.tagName === 'TEXTAREA' || 
             document.activeElement.tagName === 'INPUT' || 
             document.activeElement.getAttribute('contenteditable') === 'true')) {
            console.log('✅ [Voice] Using active element:', document.activeElement);
            cachedInput = document.activeElement as HTMLElement;
            return cachedInput;
        }

        // 3. Fallback: Global search with placeholder (Specific)
        const placeholder = "Buy groceries";
        const specificSelectors = `textarea[placeholder*="${placeholder}"], input[placeholder*="${placeholder}"], [contenteditable="true"][placeholder*="${placeholder}"]`;
        const globalMatch = document.querySelector(specificSelectors);
        if (globalMatch) {
             console.log('✅ [Voice] Found global placeholder match:', globalMatch);
             cachedInput = globalMatch as HTMLElement;
             return cachedInput;
        }
        
        console.warn('❌ [Voice] Exhausted all search strategies.');
        return null;
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalTranscript += transcript;
        else interimTranscript += transcript;
      }

      const text = finalTranscript || interimTranscript;
      if (!text) return;

      const input = findInput();
      if (!input) {
          console.warn('❌ [Voice] No input found to inject text into.');
          return;
      }

      // Injection Logic
      if (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA') {
          const el = input as HTMLInputElement | HTMLTextAreaElement;
          const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
          const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
          
          if (setter) setter.call(el, text);
          else el.value = text;
          
          el.dispatchEvent(new Event('input', { bubbles: true }));
      } else if (input.getAttribute('contenteditable') === 'true') {
          // ContentEditable injection
          input.innerText = text;
          input.dispatchEvent(new Event('input', { bubbles: true }));
      }

      // Auto-submit
      if (finalTranscript) {
          setTimeout(() => {
              // Try to find submit button near input
              let btn = input.parentElement?.querySelector('button[type="submit"]') || 
                        containerRef.current?.querySelector('button[type="submit"]');
              
              if (btn) (btn as HTMLButtonElement).click();
              else {
                  // Enter key fallback
                  input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
              }
          }, 800);
      }
    };

    recognition.onerror = (event: any) => {
        if (event.error === 'not-allowed') toast.error('Microphone access denied');
        setIsListening(false);
    };
    
    recognition.onend = () => setIsListening(false);
    recognitionRef.current = recognition;

    return () => {
        if (recognitionRef.current) try { recognitionRef.current.stop(); } catch(e) {}
    };
  }, []);

  // Toggle voice recording
  const toggleVoiceInput = useCallback(() => {
    if (!recognitionRef.current) {
      toast.error('Voice input not supported in this browser. Try Chrome.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setVoiceTranscript(''); // Clear previous
      try {
        recognitionRef.current.start();
        setIsListening(true);
        toast.info('🎤 Listening...', { duration: 1000 });
      } catch (error) {
        console.error('Failed to start recognition:', error);
        toast.error('Could not start voice input');
      }
    }
  }, [isListening]);

  // Don't render until ChatKit is ready
  if (!isReady) {
    return null;
  }

  // Closed state - floating button
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
          {/* Header buttons: Minimize & Close only */}
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="hover:bg-blue-800 p-1 rounded transition-colors"
            aria-label={isMinimized ? "Maximize" : "Minimize"}
          >
            <Minimize2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-blue-800 p-1 rounded transition-colors"
            aria-label="Close chatbot"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* ChatKit Content with Floating Mic Overlay */}
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

        {/* Floating Mic Button - Overlay on Input Area */}
        <button
            onClick={toggleVoiceInput}
            className={`absolute bottom-[20px] right-[60px] z-10 p-2 rounded-full transition-all ${
              isListening
                ? 'bg-red-500 text-white animate-pulse shadow-lg'
                : 'bg-transparent text-gray-400 hover:text-blue-600 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
            aria-label={isListening ? "Stop recording" : "Start voice input"}
            title={isListening ? "Stop recording" : "Voice input"}
        >
            {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </button>
      </div>
    </div>
  );
}

// Memoize to prevent unnecessary re-renders
export const FloatingChatbot = memo(FloatingChatbotInner);
FloatingChatbot.displayName = 'FloatingChatbot';
