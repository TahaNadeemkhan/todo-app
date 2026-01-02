# Next.js App Router Examples

## Server Component with Data Fetching

```tsx
// app/tasks/page.tsx (Server Component)
import { TaskCard } from '@/components/tasks/task-card'

export default async function TasksPage() {
  const res = await fetch('http://localhost:8000/api/v1/tasks', {
    cache: 'no-store',
  })
  const tasks = await res.json()

  return (
    <div className="grid gap-4">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  )
}
```

## Client Component with Interactivity

```tsx
// components/tasks/delete-button.tsx
'use client'

import { useTransition } from 'react'
import { Button } from '@/components/ui/button'
import { deleteTask } from '@/app/tasks/actions'

export function DeleteButton({ taskId }: { taskId: string }) {
  const [isPending, startTransition] = useTransition()

  return (
    <Button
      variant="destructive"
      disabled={isPending}
      onClick={() => startTransition(() => deleteTask(taskId))}
    >
      {isPending ? 'Deleting...' : 'Delete'}
    </Button>
  )
}
```

## Server Actions

```tsx
// app/tasks/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createTask(formData: FormData) {
  const title = formData.get('title') as string
  const priority = formData.get('priority') as string

  await fetch('http://localhost:8000/api/v1/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, priority }),
  })

  revalidatePath('/tasks')
}

export async function deleteTask(taskId: string) {
  await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
    method: 'DELETE',
  })
  revalidatePath('/tasks')
}

export async function completeTask(taskId: string) {
  await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: 'completed' }),
  })
  revalidatePath('/tasks')
}
```

## Form with Server Action

```tsx
// app/tasks/new/page.tsx (Server Component)
import { createTask } from '../actions'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function NewTaskPage() {
  return (
    <form action={createTask} className="space-y-4">
      <Input name="title" placeholder="Task title" required />
      <select name="priority" className="border rounded p-2">
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <Button type="submit">Create Task</Button>
    </form>
  )
}
```

## Layout Structure

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b p-4">
          <a href="/">Todo App</a>
        </nav>
        <main className="container mx-auto p-4">{children}</main>
      </body>
    </html>
  )
}
```
