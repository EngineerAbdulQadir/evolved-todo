---
name: react-components
description: React 18+ component patterns, hooks, composition, Server/Client Components, and TypeScript integration.
---

# React Components

## Instructions

### When to Use

- Creating reusable React components
- Implementing custom hooks
- Managing component state with hooks
- Composing components with proper patterns
- Implementing Server Components vs Client Components
- Writing type-safe components with TypeScript

## Functional Components with TypeScript

### Basic Component

```typescript
// components/Button.tsx
interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  onClick?: () => void
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  disabled = false,
  type = 'button',
}: ButtonProps) {
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded font-medium transition ${variantClasses[variant]} ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {children}
    </button>
  )
}
```

### Component with State

```typescript
// components/Counter.tsx
'use client'

import { useState } from 'react'

interface CounterProps {
  initialCount?: number
  step?: number
  min?: number
  max?: number
}

export function Counter({
  initialCount = 0,
  step = 1,
  min = -Infinity,
  max = Infinity,
}: CounterProps) {
  const [count, setCount] = useState(initialCount)

  const increment = () => {
    setCount(prev => Math.min(prev + step, max))
  }

  const decrement = () => {
    setCount(prev => Math.max(prev - step, min))
  }

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={decrement}
        disabled={count <= min}
        className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
      >
        -
      </button>

      <span className="text-2xl font-bold">{count}</span>

      <button
        onClick={increment}
        disabled={count >= max}
        className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
      >
        +
      </button>
    </div>
  )
}
```

## React Hooks

### useState - State Management

```typescript
// components/TaskForm.tsx
'use client'

import { useState } from 'react'

export function TaskForm() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log({ title, description, priority })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />
      <select value={priority} onChange={(e) => setPriority(e.target.value as any)}>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <button type="submit">Create Task</button>
    </form>
  )
}
```

### useEffect - Side Effects

```typescript
// components/TaskList.tsx
'use client'

import { useState, useEffect } from 'react'
import type { Task } from '@/lib/api-types'

export function TaskList({ userId }: { userId: number }) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true)
        const response = await fetch(`/api/${userId}/tasks`)
        const data = await response.json()
        setTasks(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch tasks')
      } finally {
        setLoading(false)
      }
    }

    fetchTasks()
  }, [userId]) // Re-fetch when userId changes

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  )
}
```

### useContext - Global State

```typescript
// contexts/ThemeContext.tsx
'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextType {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light')

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={theme}>
        {children}
      </div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

// Usage
function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  )
}
```

### Custom Hooks

```typescript
// hooks/useTasks.ts
import { useState, useEffect } from 'react'
import type { Task } from '@/lib/api-types'
import { tasksApi } from '@/lib/api-client'

export function useTasks(userId: number, completed?: boolean) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    const fetchTasks = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await tasksApi.list(userId, completed)

        if (!cancelled) {
          setTasks(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch tasks'))
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchTasks()

    return () => {
      cancelled = true
    }
  }, [userId, completed])

  const refresh = async () => {
    setLoading(true)
    try {
      const data = await tasksApi.list(userId, completed)
      setTasks(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to refresh tasks'))
    } finally {
      setLoading(false)
    }
  }

  return { tasks, loading, error, refresh }
}

// Usage
function TaskListWithHook({ userId }: { userId: number }) {
  const { tasks, loading, error, refresh } = useTasks(userId)

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <button onClick={refresh}>Refresh</button>
      <ul>
        {tasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

## Component Composition

### Compound Components

```typescript
// components/Card/Card.tsx
interface CardProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {children}
    </div>
  )
}

// components/Card/CardHeader.tsx
export function CardHeader({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-6 py-4 border-b border-gray-200">
      {children}
    </div>
  )
}

// components/Card/CardBody.tsx
export function CardBody({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-6 py-4">
      {children}
    </div>
  )
}

// components/Card/CardFooter.tsx
export function CardFooter({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-6 py-4 border-t border-gray-200">
      {children}
    </div>
  )
}

// components/Card/index.ts
export { Card } from './Card'
export { CardHeader } from './CardHeader'
export { CardBody } from './CardBody'
export { CardFooter } from './CardFooter'

// Usage
import { Card, CardHeader, CardBody, CardFooter } from '@/components/Card'

function TaskCard({ task }: { task: Task }) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-bold">{task.title}</h3>
      </CardHeader>
      <CardBody>
        <p>{task.description}</p>
      </CardBody>
      <CardFooter>
        <span className="text-sm text-gray-500">
          Created: {new Date(task.created_at).toLocaleDateString()}
        </span>
      </CardFooter>
    </Card>
  )
}
```

### Render Props Pattern

```typescript
// components/DataLoader.tsx
interface DataLoaderProps<T> {
  fetch: () => Promise<T>
  children: (data: T) => React.ReactNode
  loading?: React.ReactNode
  error?: (error: Error) => React.ReactNode
}

export function DataLoader<T>({
  fetch,
  children,
  loading = <div>Loading...</div>,
  error = (err) => <div>Error: {err.message}</div>,
}: DataLoaderProps<T>) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [err, setErr] = useState<Error | null>(null)

  useEffect(() => {
    fetch()
      .then(setData)
      .catch(setErr)
      .finally(() => setIsLoading(false))
  }, [fetch])

  if (isLoading) return <>{loading}</>
  if (err) return <>{error(err)}</>
  if (!data) return null

  return <>{children(data)}</>
}

// Usage
<DataLoader
  fetch={() => tasksApi.list(userId)}
  loading={<Spinner />}
  error={(err) => <Alert variant="error">{err.message}</Alert>}
>
  {(tasks) => (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  )}
</DataLoader>
```

## Performance Optimization

### React.memo

```typescript
// components/TaskItem.tsx
import { memo } from 'react'

interface TaskItemProps {
  task: Task
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export const TaskItem = memo(function TaskItem({
  task,
  onToggle,
  onDelete,
}: TaskItemProps) {
  return (
    <div className="flex items-center gap-4 p-4 border rounded">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      <span className={task.completed ? 'line-through text-gray-500' : ''}>
        {task.title}
      </span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  )
})
```

### useMemo & useCallback

```typescript
// components/TaskList.tsx
'use client'

import { useState, useMemo, useCallback } from 'react'

export function TaskList({ tasks }: { tasks: Task[] }) {
  const [filter, setFilter] = useState<'all' | 'completed' | 'active'>('all')

  // Memoize filtered tasks (expensive computation)
  const filteredTasks = useMemo(() => {
    switch (filter) {
      case 'completed':
        return tasks.filter(t => t.completed)
      case 'active':
        return tasks.filter(t => !t.completed)
      default:
        return tasks
    }
  }, [tasks, filter])

  // Memoize callback to prevent re-renders
  const handleToggle = useCallback((id: number) => {
    // Toggle task completion
  }, [])

  return (
    <div>
      <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>

      {filteredTasks.map(task => (
        <TaskItem key={task.id} task={task} onToggle={handleToggle} />
      ))}
    </div>
  )
}
```

## Server vs Client Components (Next.js 16+)

### Server Component (Default)

```typescript
// app/tasks/page.tsx (Server Component)
import { tasksApi } from '@/lib/api-client'

export default async function TasksPage() {
  // Server-side data fetching
  const tasks = await tasksApi.list(1)

  return (
    <div>
      <h1>Tasks</h1>
      <ul>
        {tasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

### Client Component

```typescript
// components/TaskForm.tsx (Client Component)
'use client'

import { useState } from 'react'

export function TaskForm() {
  const [title, setTitle] = useState('')

  return (
    <form>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
    </form>
  )
}
```

## Integration with frontend-react-dev Subagent

This skill is primarily used by:
- **frontend-react-dev** - For implementing React components
- **ux-advocate** - For component UX patterns

### Key Principles

1. **Functional Components** - Always use functional components, never class components
2. **TypeScript Props** - All props must have TypeScript interfaces
3. **Hooks** - Use hooks for state and side effects
4. **Composition** - Build complex UIs from simple components
5. **Performance** - Use memo, useMemo, useCallback when needed
6. **Server First** - Default to Server Components in Next.js
