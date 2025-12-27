---
name: phase-scaffolder
description: Create standardized directory structures for new project phases (History, Specs, Source). Use when the user starts a new phase like "Phase 2" or "Phase 3".
allowed-tools: Bash, Write, Read
---

# Phase Scaffolder Skill

## Purpose

To enforce a consistent folder structure across the "Evolution of Todo" project lifecycle.

## Naming Conventions

- **History/Prompts:** `history/prompts/{NNN}-{phase}-{slug}` (e.g., `002-phase2-web-app`)
- **Specs:** `specs/{NNN}-{phase}-{slug}` (e.g., `002-phase2-web-app`)
- **Source:** `todo_app/phase_{N}` (e.g., `phase_2`)

## Instructions

When the user asks to "Start Phase X", perform the following actions using the `Bash` tool:

1. **Identify Variables:**
   - `N`: The phase number (e.g., 2).
   - `NNN`: The padded number (e.g., 002).
   - `SLUG`: A short description (e.g., `web-app` for Phase 2).

2. **Create Directories:**
   - Create `history/prompts/{NNN}-phase{N}-{SLUG}/`
   - Create `specs/{NNN}-phase{N}-{SLUG}/`
   - Create `todo_app/phase_{N}/`

3. **Initialize Files:**
   - Create a `.gitkeep` or `README.md` in each new folder to ensure they are tracked.
   - Inside `specs/.../`, create a blank `spec.md` and `plan.md`.
   - Inside `todo_app/phase_{N}/`, create an empty `src` folder.

## Example Usage

User: "Setup Phase 2 for Web App"
Action:
- `mkdir -p history/prompts/002-phase2-web-app`
- `mkdir -p specs/002-phase2-web-app`
- `mkdir -p todo_app/phase_2/src`
