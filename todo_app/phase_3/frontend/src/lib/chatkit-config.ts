/**
 * ChatKit Configuration
 * Theme and settings from ChatKit Studio Playground
 */

import type { ChatKitOptions } from "@openai/chatkit-react";

// ChatKit API endpoint (proxied through Next.js API route)
export const CHATKIT_API_URL = process.env.NEXT_PUBLIC_CHATKIT_API_URL || "/api/chatkit";

// ChatKit domain key (REQUIRED)
export const CHATKIT_API_DOMAIN_KEY =
  process.env.NEXT_PUBLIC_CHATKIT_API_DOMAIN_KEY || "domain_pk_localhost_dev";

// Complete ChatKit configuration matching ChatKit Studio design
export const getChatKitOptions = (): ChatKitOptions => ({
  api: {
    url: CHATKIT_API_URL,
    domainKey: CHATKIT_API_DOMAIN_KEY,
  },
  theme: {
    colorScheme: 'dark',
    radius: 'round',
    density: 'normal',
    typography: {
      baseSize: 16,
      fontFamily: '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
      fontFamilyMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
      fontSources: [
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
          weight: 400,
          style: 'normal',
          display: 'swap'
        },
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Medium.woff2',
          weight: 500,
          style: 'normal',
          display: 'swap'
        },
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-SemiBold.woff2',
          weight: 600,
          style: 'normal',
          display: 'swap'
        },
        {
          family: 'OpenAI Sans',
          src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Bold.woff2',
          weight: 700,
          style: 'normal',
          display: 'swap'
        }
      ]
    }
  },
  composer: {
    placeholder: "e.g. Add 'Buy groceries'",
    attachments: {
      enabled: false
    },
  },
  startScreen: {
    greeting: 'Welcome to iTasks 🚀 Let\'s plan your day and get things done',
    prompts: [
      {
        label: 'Add a new task',
        prompt: 'Add a task to buy groceries tomorrow'
      },
      {
        label: 'Show my tasks',
        prompt: 'Show me all my tasks for today'
      },
      {
        label: 'Complete a task',
        prompt: 'Mark my first task as complete'
      },
      {
        label: 'Task suggestions',
        prompt: 'What tasks should I work on next?'
      }
    ],
  },
});
