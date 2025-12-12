/**
 * Better Auth server configuration.
 * Configures authentication with email/password and JWT for API access.
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: true, // Neon requires SSL
    max: 2, // Limit pool size to prevent connection exhaustion in serverless/dev envs
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 5000,
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
        expiresIn: "7d",
        issuer: "todo-app",
        audience: "todo-app-api",
      },
    }),
  ],
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;