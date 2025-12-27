---
id: 0009
title: Final Deployment Vercel Railway
stage: misc
date: 2025-12-16
surface: agent
model: Claude Sonnet 4.5
feature: 002-phase2-web-app
branch: master
user: TahaNadeemKhan
command: /sp.phr
labels: ["deployment", "vercel", "railway", "production", "brevo-email", "ui-redesign", "authentication"]
links:
  spec: https://github.com/TahaNadeemkhan/todo-app/blob/master/specs/002-phase2-web-app/spec.md
  ticket: null
  adr: null
  pr: https://github.com/TahaNadeemkhan/todo-app/pulls
files:
  - todo_app/phase_2/frontend/src/app/login/page.tsx
  - todo_app/phase_2/frontend/src/app/register/page.tsx
  - todo_app/phase_2/frontend/src/app/page.tsx
  - todo_app/phase_2/frontend/src/lib/auth.ts
  - todo_app/phase_2/frontend/src/lib/api.ts
  - todo_app/phase_2/frontend/src/middleware.ts
  - todo_app/phase_2/backend/src/todo_app/services/email_service.py
  - todo_app/phase_2/backend/src/todo_app/config.py
  - todo_app/phase_2/backend/src/todo_app/db.py
  - todo_app/phase_2/backend/src/todo_app/main.py
  - todo_app/phase_2/backend/pyproject.toml
tests:
  - Manual testing of login/register flow on Vercel production
  - Email notification testing with Brevo API
  - Database connection pooling testing on Railway
  - CORS and authentication flow testing
---

## Prompt

please record a phr for my final deployement on vercel and railway

## Response snapshot

Completed full-stack deployment of Phase 2 Todo App to production. Frontend deployed to Vercel (https://itask-chi.vercel.app) with Better Auth authentication. Backend deployed to Railway with Brevo email integration (300 emails/day free tier). Redesigned login/register pages with consistent blue-purple gradient theme across all pages. Fixed production issues including CORS configuration, SMTP blocking (switched to Brevo API), database connection pooling for Neon serverless, and authentication cookie handling.

## Outcome

- ✅ Impact: Successfully deployed production-ready full-stack Todo app with professional UI, working authentication, email notifications, and database persistence. App is live and functional at https://itask-chi.vercel.app
- 🧪 Tests: Manual testing of login/register flows, task CRUD operations, email notifications via Brevo, database cold start handling, and cross-origin authentication
- 📁 Files: Modified 11 core files including authentication, API client, email service, database configuration, and all auth pages
- 🔁 Next prompts: Consider cleaning unused database tables (verification table), add email verification flow, implement rate limiting, add monitoring/analytics, optimize bundle size
- 🧠 Reflection: Railway blocks SMTP ports requiring API-based email service (Brevo). Neon serverless needs robust connection pooling and retry logic. Consistent theme across pages significantly improves professional appearance.

## Evaluation notes (flywheel)

- Failure modes observed: Initial SMTP blocking on Railway not anticipated; required pivot to Brevo API. Frontend CORS issues with Vercel preview deployments vs production URL. Neon cold starts causing "failed to load tasks" errors requiring connection pooling and retry logic. Theme inconsistency initially made app look unprofessional.
- Graders run and results (PASS/FAIL): PASS - Authentication works in production. PASS - Email notifications delivered via Brevo. PASS - Database queries succeed with connection pooling. PASS - UI theme consistent across all pages. PASS - CORS properly configured for production domain.
- Prompt variant (if applicable): N/A - Final deployment documentation
- Next experiment (smallest change to try): Add basic monitoring/logging to track production errors and performance metrics. Consider implementing email verification using existing verification table.
