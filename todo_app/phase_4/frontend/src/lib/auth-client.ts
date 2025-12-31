/**
 * Better Auth client for frontend usage.
 * Provides authentication methods for React components.
 */

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

// Export commonly used hooks and methods
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

/**
 * Get JWT token for API requests to FastAPI backend.
 * Returns null if not authenticated.
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const response = await authClient.token();
    return response.data?.token || null;
  } catch {
    return null;
  }
}
