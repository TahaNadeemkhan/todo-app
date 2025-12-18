/**
 * Better Auth server configuration.
 * Configures authentication with email/password and JWT for API access.
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Determine the base URL for Better Auth
const getBaseURL = () => {
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "http://localhost:3000";
};

export const auth = betterAuth({
  baseURL: getBaseURL(),
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false, // Allow self-signed certs for Neon
    },
    max: 3, // Slightly larger pool
    idleTimeoutMillis: 60000, // 60 seconds idle timeout
    connectionTimeoutMillis: 30000, // 30 seconds connection timeout (increased)
    keepAlive: true, // Keep connection alive
  }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
        issuer: "todo-app",
        audience: "todo-app-api",
      },
    }),
  ],
  trustedOrigins: ["https://itask-chi.vercel.app", "http://localhost:3000"],
  advanced: {
    crossSubDomainCookies: {
      enabled: false,
    },
    defaultCookieAttributes: {
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
    },
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;