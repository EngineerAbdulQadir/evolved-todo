---
name: tailwind-design
description: Tailwind CSS best practices, utility-first design, responsive patterns, and component styling.
---

# Tailwind CSS Design

## Instructions

### When to Use

- Styling React components with Tailwind CSS
- Implementing responsive designs
- Creating component variants with utility classes
- Building dark mode support
- Designing accessible interfaces
- Optimizing class patterns for performance

## Utility-First CSS

### Basic Styling

```typescript
// components/Button.tsx
export function Button({ children, onClick }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors"
    >
      {children}
    </button>
  )
}
```

### Component Variants

```typescript
// components/Alert.tsx
interface AlertProps {
  variant: 'info' | 'success' | 'warning' | 'error'
  children: React.ReactNode
}

export function Alert({ variant, children }: AlertProps) {
  const variantClasses = {
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    error: 'bg-red-50 text-red-800 border-red-200',
  }

  return (
    <div className={`p-4 border rounded-lg ${variantClasses[variant]}`}>
      {children}
    </div>
  )
}
```

## Responsive Design

### Mobile-First Breakpoints

```typescript
// components/Card.tsx
export function Card({ title, children }: CardProps) {
  return (
    <div className="
      w-full
      sm:w-96
      md:w-1/2
      lg:w-1/3
      xl:w-1/4
      p-4
      sm:p-6
      bg-white
      rounded-lg
      shadow-md
    ">
      <h3 className="text-lg sm:text-xl md:text-2xl font-bold mb-4">
        {title}
      </h3>
      {children}
    </div>
  )
}
```

**Breakpoints:**
- `sm`: 640px (small devices)
- `md`: 768px (tablets)
- `lg`: 1024px (laptops)
- `xl`: 1280px (desktops)
- `2xl`: 1536px (large desktops)

### Responsive Grid

```typescript
// components/TaskGrid.tsx
export function TaskGrid({ tasks }: { tasks: Task[] }) {
  return (
    <div className="
      grid
      grid-cols-1
      sm:grid-cols-2
      md:grid-cols-3
      lg:grid-cols-4
      gap-4
      p-4
    ">
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  )
}
```

## Color Palette and Theming

### Custom Color Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Base color
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          // Custom secondary colors
        }
      }
    }
  }
}
```

### Using Custom Colors

```typescript
// components/PrimaryButton.tsx
export function PrimaryButton({ children }: { children: React.ReactNode }) {
  return (
    <button className="
      px-4 py-2
      bg-primary-600
      hover:bg-primary-700
      active:bg-primary-800
      text-white
      font-medium
      rounded-lg
      transition-colors
    ">
      {children}
    </button>
  )
}
```

## Dark Mode Support

### Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
  theme: {
    extend: {}
  }
}
```

### Dark Mode Classes

```typescript
// components/Card.tsx
export function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="
      bg-white dark:bg-gray-800
      text-gray-900 dark:text-gray-100
      border border-gray-200 dark:border-gray-700
      rounded-lg
      shadow-md
      p-6
    ">
      {children}
    </div>
  )
}
```

### Dark Mode Toggle

```typescript
// components/ThemeToggle.tsx
'use client'

import { useState, useEffect } from 'react'

export function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true)
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleTheme = () => {
    if (darkMode) {
      document.documentElement.classList.remove('dark')
      setDarkMode(false)
    } else {
      document.documentElement.classList.add('dark')
      setDarkMode(true)
    }
  }

  return (
    <button
      onClick={toggleTheme}
      className="
        p-2
        rounded-lg
        bg-gray-200 dark:bg-gray-700
        hover:bg-gray-300 dark:hover:bg-gray-600
        transition-colors
      "
    >
      {darkMode ? '🌙' : '☀️'}
    </button>
  )
}
```

## Layout Patterns

### Flexbox Layout

```typescript
// components/Header.tsx
export function Header() {
  return (
    <header className="
      flex
      items-center
      justify-between
      px-6
      py-4
      bg-white
      border-b
      border-gray-200
    ">
      <div className="flex items-center gap-4">
        <Logo />
        <Nav />
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  )
}
```

### Grid Layout

```typescript
// app/(dashboard)/layout.tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="
      min-h-screen
      grid
      grid-rows-[auto_1fr_auto]
      md:grid-cols-[250px_1fr]
      md:grid-rows-[auto_1fr]
    ">
      {/* Header - spans full width */}
      <header className="md:col-span-2">
        <Header />
      </header>

      {/* Sidebar - hidden on mobile */}
      <aside className="hidden md:block bg-gray-50 border-r border-gray-200">
        <Sidebar />
      </aside>

      {/* Main content */}
      <main className="p-6">
        {children}
      </main>
    </div>
  )
}
```

## Spacing and Typography

### Consistent Spacing

```typescript
// components/TaskCard.tsx
export function TaskCard({ task }: { task: Task }) {
  return (
    <div className="space-y-4 p-6 bg-white rounded-lg shadow">
      {/* space-y-4 adds vertical spacing between children */}
      <h3 className="text-xl font-bold">{task.title}</h3>
      <p className="text-gray-600">{task.description}</p>
      <div className="flex gap-2">
        {/* gap-2 adds horizontal spacing in flex */}
        <Badge>{task.priority}</Badge>
        <Badge>{task.completed ? 'Done' : 'Active'}</Badge>
      </div>
    </div>
  )
}
```

### Typography Scale

```typescript
// components/Typography.tsx
export function Heading({ level, children }: { level: 1 | 2 | 3 | 4; children: React.ReactNode }) {
  const sizes = {
    1: 'text-4xl font-bold',
    2: 'text-3xl font-bold',
    3: 'text-2xl font-semibold',
    4: 'text-xl font-semibold',
  }

  const Tag = `h${level}` as keyof JSX.IntrinsicElements

  return <Tag className={sizes[level]}>{children}</Tag>
}
```

## Accessibility

### Focus States

```typescript
// components/Button.tsx
export function Button({ children, onClick }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className="
        px-4 py-2
        bg-blue-600
        text-white
        rounded-lg
        hover:bg-blue-700
        focus:outline-none
        focus:ring-2
        focus:ring-blue-500
        focus:ring-offset-2
        transition-all
      "
    >
      {children}
    </button>
  )
}
```

### Screen Reader Classes

```typescript
// components/SkipLink.tsx
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="
        sr-only
        focus:not-sr-only
        focus:absolute
        focus:top-4
        focus:left-4
        focus:z-50
        focus:px-4
        focus:py-2
        focus:bg-blue-600
        focus:text-white
        focus:rounded
      "
    >
      Skip to main content
    </a>
  )
}
```

## Animations and Transitions

### Hover Effects

```typescript
// components/Card.tsx
export function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="
      p-6
      bg-white
      rounded-lg
      shadow-md
      hover:shadow-xl
      hover:-translate-y-1
      transition-all
      duration-300
      ease-in-out
    ">
      {children}
    </div>
  )
}
```

### Loading States

```typescript
// components/Skeleton.tsx
export function Skeleton() {
  return (
    <div className="
      h-32
      bg-gray-200
      rounded-lg
      animate-pulse
    " />
  )
}
```

## Component Class Patterns

### Class Variance Authority (CVA)

```bash
pnpm add class-variance-authority clsx
```

```typescript
// components/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { clsx } from 'clsx'

const buttonVariants = cva(
  'px-4 py-2 font-medium rounded-lg transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
        danger: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm: 'text-sm px-3 py-1',
        md: 'text-base px-4 py-2',
        lg: 'text-lg px-6 py-3',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

interface ButtonProps extends VariantProps<typeof buttonVariants> {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export function Button({
  variant,
  size,
  children,
  onClick,
  className,
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(buttonVariants({ variant, size }), className)}
    >
      {children}
    </button>
  )
}

// Usage
<Button variant="primary" size="lg">Click me</Button>
<Button variant="danger" size="sm">Delete</Button>
```

## Form Styling

### Input Components

```typescript
// components/Input.tsx
interface InputProps {
  label: string
  error?: string
  type?: string
  value: string
  onChange: (value: string) => void
}

export function Input({ label, error, type = 'text', value, onChange }: InputProps) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>

      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={clsx(
          'w-full px-3 py-2 border rounded-lg',
          'focus:outline-none focus:ring-2',
          error
            ? 'border-red-300 focus:ring-red-500'
            : 'border-gray-300 focus:ring-blue-500'
        )}
      />

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}
```

## Performance Optimization

### Avoid Dynamic Classes

```typescript
// ❌ Bad: Dynamic classes (not purged correctly)
<div className={`text-${color}-600`}>

// ✅ Good: Use full class names
<div className={
  color === 'blue' ? 'text-blue-600' :
  color === 'red' ? 'text-red-600' :
  'text-gray-600'
}>
```

### Use @apply Sparingly

```css
/* ❌ Bad: Overusing @apply defeats utility-first purpose */
.button {
  @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
}

/* ✅ Good: Use utilities directly in components */
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
```

## Integration with frontend-react-dev Subagent

This skill is primarily used by:
- **frontend-react-dev** - For styling React components
- **ux-advocate** - For accessible, user-friendly designs

### Key Principles

1. **Utility-First** - Compose designs from utility classes
2. **Mobile-First** - Design for mobile, then scale up
3. **Consistent Spacing** - Use Tailwind's spacing scale
4. **Dark Mode** - Support dark mode with `dark:` variant
5. **Accessibility** - Use focus states and screen reader classes
6. **Performance** - Avoid dynamic class names for proper purging
