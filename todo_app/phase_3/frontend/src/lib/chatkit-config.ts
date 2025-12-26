/**
 * ChatKit Configuration
 * CORRECTED for actual ChatKit API schema
 */

// ChatKit API endpoint (proxied through Next.js in development)
export const CHATKIT_API_URL = process.env.NEXT_PUBLIC_CHATKIT_API_URL || "/api/chatkit";

// ChatKit domain key (REQUIRED)
export const CHATKIT_API_DOMAIN_KEY =
  process.env.NEXT_PUBLIC_CHATKIT_API_DOMAIN_KEY || "domain_pk_localhost_dev";

// MINIMAL VALID CONFIGURATION
// Start with basics that ChatKit accepts
export const CHATKIT_THEME = undefined;
export const CHATKIT_COMPOSER = undefined;
export const CHATKIT_START_SCREEN = undefined;
