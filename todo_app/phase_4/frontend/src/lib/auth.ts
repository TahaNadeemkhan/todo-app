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
    connectionString: process.env.DATABASE_URL + "&connect_timeout=10&statement_timeout=10000",
    ssl: {
      rejectUnauthorized: false, // Allow self-signed certs for Neon
    },
    max: 2,
    idleTimeoutMillis: 20000,
    connectionTimeoutMillis: 10000, // 10 seconds for initial connection
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