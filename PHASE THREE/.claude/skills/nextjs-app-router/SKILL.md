# Next.js 16+ App Router Patterns

**Skill**: nextjs-app-router
**Version**: 1.0.0
**Primary Users**: nextjs-chatkit-implementer
**Prerequisites**: Next.js 16+, React 18+, TypeScript

## Purpose
Build Next.js 16+ applications using App Router with Server/Client Components, Route Groups, and Server Actions.

## Core Patterns

### App Router Structure
```
frontend/app/
├── (auth)/              # Route Group (affects layout, not URL)
│   ├── login/
│   │   └── page.tsx
│   └── signup/
│       └── page.tsx
├── (app)/               # Authenticated app routes
│   ├── chat/
│   │   └── page.tsx     # /chat
│   └── layout.tsx       # Layout for authenticated routes
└── layout.tsx           # Root layout
```

### Server vs Client Components
```typescript
// Server Component (default) - can fetch data server-side
// app/(app)/chat/page.tsx
export default async function ChatPage() {
  // Can use async/await for server-side data fetching
  const data = await fetchServerData();
  
  return (
    <div>
      <ChatInterface /> {/* Client Component */}
    </div>
  );
}

// Client Component - use 'use client' directive
// components/chat/ChatInterface.tsx
'use client';

import { useState } from 'react';

export function ChatInterface() {
  const [messages, setMessages] = useState([]);
  
  return <div>{/* Interactive UI */}</div>;
}
```

### Route Groups
```typescript
// (auth) and (app) are route groups - they don't affect URLs
// But allow different layouts:

// app/(auth)/layout.tsx - Layout for auth pages (no sidebar)
export default function AuthLayout({ children }) {
  return <div className="auth-layout">{children}</div>;
}

// app/(app)/layout.tsx - Layout for app pages (with sidebar)
export default function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}
```

### Server Actions (for forms)
```typescript
// app/(app)/chat/actions.ts
'use server';

export async function sendMessage(formData: FormData) {
  const message = formData.get('message');
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
  return response.json();
}

// app/(app)/chat/page.tsx
import { sendMessage } from './actions';

export default function ChatPage() {
  return (
    <form action={sendMessage}>
      <input name="message" />
      <button type="submit">Send</button>
    </form>
  );
}
```

### Loading States
```typescript
// app/(app)/chat/loading.tsx - Shown while page loads
export default function Loading() {
  return <div>Loading chat...</div>;
}
```

### Error Boundaries
```typescript
// app/(app)/chat/error.tsx
'use client';

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

### Authentication Guard
```typescript
// app/(app)/layout.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function AppLayout({ children }) {
  const session = await getSession();
  
  if (!session) {
    redirect('/login');
  }
  
  return <div>{children}</div>;
}
```

## Best Practices
- Use Server Components by default (async data fetching)
- Add 'use client' only when needed (interactivity, hooks)
- Use Route Groups for shared layouts without affecting URLs
- Create loading.tsx and error.tsx for better UX
- Use Server Actions for form submissions
- Implement authentication checks in layout.tsx

## File Naming Conventions
- `page.tsx` - Page component (required for route)
- `layout.tsx` - Shared layout wrapper
- `loading.tsx` - Loading UI while page loads
- `error.tsx` - Error boundary component
- `not-found.tsx` - 404 page
- `route.ts` - API route handler

## Related Skills
react-components, tailwind-design, better-auth-jwt

See examples.md for complete Next.js 16+ patterns.
