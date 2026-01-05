---
name: nextjs-app-router
description: Build frontend using Next.js 15+ App Router. Use when creating pages, layouts, components, or client interactions. Triggers on mentions of Next.js, React, frontend, pages, routing, Server Components, or Server Actions.
---

# Next.js App Router Skill

## Mandatory Rules

### 1. Directory Structure (REQUIRED)

Use `src/app/` directory:

```
src/app/
├── layout.tsx      # Root layout (Server Component)
├── page.tsx        # Home page
├── tasks/
│   ├── page.tsx    # /tasks
│   ├── [id]/page.tsx
│   └── actions.ts  # Server Actions
```

### 2. Server Components by Default (REQUIRED)

Components are Server Components unless they need interactivity:

```tsx
// Server Component (default) - async data fetching
export default async function TasksPage() {
  const tasks = await fetch('http://api/tasks').then(r => r.json())
  return <TaskList tasks={tasks} />
}
```

### 3. Client Components Only for Interactivity (REQUIRED)

Add `'use client'` ONLY when using hooks, events, or browser APIs:

```tsx
'use client'
import { useState } from 'react'

export function TaskActions({ taskId }: { taskId: string }) {
  const [loading, setLoading] = useState(false)
  return <button onClick={() => setLoading(true)}>Complete</button>
}
```

### 4. Server Actions for Mutations (REQUIRED)

Use Server Actions instead of API routes:

```tsx
// app/tasks/actions.ts
'use server'
import { revalidatePath } from 'next/cache'

export async function createTask(formData: FormData) {
  await fetch('http://api/tasks', {
    method: 'POST',
    body: JSON.stringify({ title: formData.get('title') }),
  })
  revalidatePath('/tasks')
}
```

### 5. Shadcn/UI Components (REQUIRED)

Use Shadcn/UI for consistent UI:

```bash
npx shadcn@latest add button card input
```

For detailed examples, see [examples.md](examples.md).

## Checklist

- [ ] Using `src/app/` directory structure
- [ ] Components are Server Components by default
- [ ] `'use client'` ONLY for hooks/events/browser APIs
- [ ] Server Actions for mutations (not API routes)
- [ ] Shadcn/UI for UI components
