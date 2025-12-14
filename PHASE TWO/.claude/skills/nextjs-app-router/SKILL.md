---
name: nextjs-app-router
description: Next.js 16+ App Router patterns, Route Groups, Server/Client Components, Server Actions, and App Router best practices.
---

# Next.js App Router

## Instructions

### When to Use

- Setting up Next.js App Router structure and layouts
- Creating Server Components vs Client Components
- Implementing Route Groups for logical organization
- Using Server Actions for mutations
- Implementing loading and error UI patterns
- Setting up metadata and SEO optimization

## App Router File Conventions

```
app/
├── layout.tsx              # Root layout (required)
├── page.tsx                # Home page
├── loading.tsx             # Loading UI (Suspense fallback)
├── error.tsx               # Error boundary
├── not-found.tsx           # 404 page
├── (auth)/                 # Route Group (doesn't affect URL)
│   ├── layout.tsx          # Auth layout
│   ├── login/
│   │   └── page.tsx        # /login
│   └── register/
│       └── page.tsx        # /register
└── (dashboard)/            # Route Group
    ├── layout.tsx          # Dashboard layout
    ├── tasks/
    │   ├── page.tsx        # /tasks
    │   ├── [id]/
    │   │   └── page.tsx    # /tasks/[id]
    │   └── loading.tsx     # Tasks loading UI
    └── profile/
        └── page.tsx        # /profile
```

## Server Components vs Client Components

### Server Components (Default)

**Use when:**
- Fetching data from APIs or databases
- Accessing backend resources directly
- Keeping large dependencies on the server
- Keeping sensitive information secure (API keys, tokens)

```typescript
// app/tasks/page.tsx (Server Component by default)
import { TaskList } from '@/components/TaskList'

// Server Component - can use async/await directly
export default async function TasksPage() {
  // Direct API call on server
  const response = await fetch('http://localhost:8000/api/tasks', {
    cache: 'no-store', // or 'force-cache', or { next: { revalidate: 3600 } }
  })
  const tasks = await response.json()

  return <TaskList tasks={tasks} />
}

// Generate metadata
export async function generateMetadata() {
  return {
    title: 'Tasks | Todo App',
    description: 'Manage your tasks efficiently',
  }
}
```

### Client Components

**Use when:**
- Using browser APIs (localStorage, window, navigator)
- Event handlers (onClick, onChange, onSubmit)
- React hooks (useState, useEffect, useContext)
- Client-side interactivity and animations

```typescript
// app/tasks/TaskForm.tsx (Client Component)
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export function TaskForm() {
  const [title, setTitle] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await fetch('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ title }),
    })
    router.refresh() // Refresh server data
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <button type="submit">Add Task</button>
    </form>
  )
}
```

### Best Practice: Use "use client" at the Highest Necessary Boundary

```typescript
// ✅ Good: Only TaskForm is a Client Component
// app/tasks/page.tsx (Server Component)
import { TaskList } from '@/components/TaskList'
import { TaskForm } from '@/components/TaskForm' // Client Component

export default async function TasksPage() {
  const tasks = await fetchTasks() // Server-side fetch

  return (
    <div>
      <TaskForm /> {/* Client Component bubble */}
      <TaskList tasks={tasks} /> {/* Can be Server Component */}
    </div>
  )
}

// ❌ Bad: Making entire page a Client Component unnecessarily
'use client'

export default function TasksPage() {
  // Now you can't use async/await for data fetching
  // Must use useEffect + useState instead
}
```

## Route Groups

Route Groups organize routes without affecting the URL structure:

```typescript
// app/(auth)/layout.tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      {children}
    </div>
  )
}

// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1">{children}</main>
    </div>
  )
}
```

**Benefits:**
- Different layouts for different route sections
- Logical organization without URL nesting
- Separate loading/error states per group

## Server Actions

Server Actions enable server-side mutations from Client Components:

```typescript
// app/actions/tasks.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createTask(formData: FormData) {
  const title = formData.get('title') as string

  // Server-side API call with authentication
  await fetch('http://localhost:8000/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })

  // Revalidate the tasks page cache
  revalidatePath('/tasks')
}

// app/tasks/TaskForm.tsx (Client Component)
'use client'

import { createTask } from '@/app/actions/tasks'

export function TaskForm() {
  return (
    <form action={createTask}>
      <input name="title" required />
      <button type="submit">Add Task</button>
    </form>
  )
}
```

**Benefits:**
- No need to create API routes for simple mutations
- Automatic revalidation of cached data
- Progressive enhancement (works without JS)

## Loading UI with Suspense

```typescript
// app/tasks/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      <div className="h-8 bg-gray-200 rounded animate-pulse" />
      <div className="h-8 bg-gray-200 rounded animate-pulse" />
      <div className="h-8 bg-gray-200 rounded animate-pulse" />
    </div>
  )
}

// app/tasks/page.tsx
import { Suspense } from 'react'
import { TaskList } from '@/components/TaskList'
import { TaskFilters } from '@/components/TaskFilters'

export default function TasksPage() {
  return (
    <div>
      <h1>Tasks</h1>

      {/* TaskFilters loads immediately (not async) */}
      <TaskFilters />

      {/* TaskList streams in when data is ready */}
      <Suspense fallback={<TaskListSkeleton />}>
        <TaskList />
      </Suspense>
    </div>
  )
}
```

## Error Boundaries

```typescript
// app/tasks/error.tsx
'use client' // Error boundaries must be Client Components

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="p-8 text-center">
      <h2 className="text-xl font-bold text-red-600">Something went wrong!</h2>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Try again
      </button>
    </div>
  )
}
```

## Data Fetching Patterns

### Fetch with Caching

```typescript
// Force dynamic (no cache)
const res = await fetch('http://localhost:8000/api/tasks', {
  cache: 'no-store',
})

// Cache with revalidation (ISR)
const res = await fetch('http://localhost:8000/api/tasks', {
  next: { revalidate: 3600 }, // Revalidate every hour
})

// Static (cache forever)
const res = await fetch('http://localhost:8000/api/tasks', {
  cache: 'force-cache',
})
```

### Parallel Data Fetching

```typescript
export default async function Page() {
  // Fetch in parallel
  const [tasks, user] = await Promise.all([
    fetchTasks(),
    fetchUser(),
  ])

  return (
    <div>
      <UserProfile user={user} />
      <TaskList tasks={tasks} />
    </div>
  )
}
```

## Metadata API

```typescript
// Static metadata
export const metadata = {
  title: 'Tasks | Todo App',
  description: 'Manage your tasks',
}

// Dynamic metadata
export async function generateMetadata({ params }: { params: { id: string } }) {
  const task = await fetchTask(params.id)

  return {
    title: `${task.title} | Todo App`,
    description: task.description,
  }
}
```

## Integration with frontend-react-dev Subagent

This skill is primarily used by:
- **frontend-react-dev** - For implementing Next.js App Router features
- **fullstack-integrator** - For API client patterns
- **monorepo-coordinator** - For frontend build configuration

### Key Principles

1. **Default to Server Components** - Only use Client Components when necessary
2. **Streaming with Suspense** - Show UI progressively as data loads
3. **Route Groups for Organization** - Separate concerns without URL nesting
4. **Server Actions for Mutations** - Reduce API endpoint boilerplate
5. **Proper Error Handling** - Use error.tsx boundaries
6. **Metadata for SEO** - Always define page metadata
