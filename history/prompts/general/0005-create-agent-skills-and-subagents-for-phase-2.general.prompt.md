---
id: 0005
title: Create Agent Skills and Subagents for Phase 2
stage: general
date: 2025-12-09
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: TahaNadeemKhan
command: /sp.phr
labels: ["agent-skills", "subagents", "fastapi", "sqlmodel", "nextjs", "phase2-prep"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/fastapi-design/SKILL.md
  - .claude/skills/fastapi-design/examples.md
  - .claude/skills/sqlmodel-db/SKILL.md
  - .claude/skills/nextjs-app-router/SKILL.md
  - .claude/skills/nextjs-app-router/examples.md
  - .claude/agents/backend-architect.md
  - .claude/agents/frontend-specialist.md
tests:
  - none
---

## Prompt

User requested creation of "Agent Skills" for Phase 2 development (FastAPI + Next.js) following official Claude Code documentation. Specifically:

1. **FastAPI Design Skill** (`.claude/skills/fastapi-design/SKILL.md`)
   - Enforce `Annotated` pattern for dependencies
   - Enforce Pydantic v2 `model_validate` and `model_dump`
   - Use `APIRouter` for modularity (no logic in `main.py`)
   - Strict Typing: No `Any`

2. **SQLModel Database Skill** (`.claude/skills/sqlmodel-db/SKILL.md`)
   - Use `table=True` for DB models, `table=False` for Pydantic DTOs
   - Use `session.exec(select(Model))` syntax
   - Enforce `foreign_key` constraints strictly
   - Never use raw SQL unless strictly necessary

3. **Next.js App Router Skill** (`.claude/skills/nextjs-app-router/SKILL.md`)
   - Use `src/app/` directory structure
   - Default to Server Components, `'use client'` ONLY for interactivity
   - Use Server Actions for mutations instead of API Routes
   - Use Shadcn/UI for components

Then user requested creation of 2 Subagents:

1. **Backend Architect Agent** (`.claude/agents/backend-architect.md`)
   - Skills: fastapi-design, sqlmodel-db, input-validation
   - Focus on scalability and type safety

2. **Frontend Specialist Agent** (`.claude/agents/frontend-specialist.md`)
   - Skills: nextjs-app-router
   - Focus on Next.js 15 and Tailwind CSS

## Response snapshot

Created 3 Agent Skills and 2 Subagents following official Claude Code documentation patterns. Each skill has a concise SKILL.md with mandatory rules and checklist, plus optional examples.md for progressive disclosure. Agents include YAML frontmatter with skills references, system prompts, workflows, and quality gates.

## Outcome

- ✅ Impact: Established reusable intelligence infrastructure for Phase 2 development with FastAPI backend and Next.js frontend
- 🧪 Tests: none
- 📁 Files: 7 files created (3 SKILL.md, 2 examples.md, 2 agent .md files)
- 🔁 Next prompts: Begin Phase 2 spec creation, set up FastAPI project structure, initialize Next.js app
- 🧠 Reflection: Progressive disclosure pattern (SKILL.md + examples.md) keeps context efficient while providing detailed examples when needed

## Evaluation notes (flywheel)

- Failure modes observed: Initial attempt created excessive files (dependencies.md, structure.md, .py templates) beyond official documentation pattern. User corrected to follow official structure strictly.
- Graders run and results (PASS/FAIL): PASS - Final structure follows official Claude Code Agent Skills documentation
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): When creating skills, start with minimal SKILL.md only, add examples.md only if detailed code examples are truly necessary
