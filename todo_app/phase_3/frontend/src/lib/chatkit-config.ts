/**
 * ChatKit Configuration
 * Provides settings for OpenAI ChatKit React component
 */

// ChatKit API endpoint (proxied through Next.js in development)
export const CHATKIT_API_URL = process.env.NEXT_PUBLIC_CHATKIT_API_URL || "/api/chatkit";

// ChatKit domain key for authentication
export const CHATKIT_API_DOMAIN_KEY =
  process.env.NEXT_PUBLIC_CHATKIT_API_DOMAIN_KEY || "domain_pk_localhost_dev";

// ChatKit theme configuration
export const CHATKIT_THEME = {
  colors: {
    light: {
      accent: "#398af3",
      background: "#ffffff",
      foreground: "#1f2937",
      border: "#e5e7eb",
    },
    dark: {
      accent: "#60a5fa",
      background: "#111827",
      foreground: "#f9fafb",
      border: "#374151",
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontSize: "14px",
  },
  fontSources: [
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
  ],
};

// ChatKit composer (input) configuration
export const CHATKIT_COMPOSER = {
  placeholder: "Ask me to manage your tasks... (e.g., Add 'Buy groceries')",
  attachments: false, // Disable attachments for now
};

// ChatKit start screen configuration
export const CHATKIT_START_SCREEN = {
  greeting: "Welcome to iTasks! 🎯",
  suggestedPrompts: [
    "Add a new task to my list",
    "Show my tasks for today",
    "Mark 'Buy groceries' as complete",
    "What are my pending tasks?",
    "Delete completed tasks",
  ],
};
