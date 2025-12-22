# ADR-008: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 002-phase2-web-app
- **Context:** Phase 2 requires a modern, performant frontend with server-side rendering, static generation, authentication, and excellent developer experience. The stack must support TypeScript strict mode, component reusability, responsive design, and seamless integration with Better Auth for JWT authentication.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines all frontend development patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Next.js vs Remix vs Vite+React
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all UI development
-->

## Decision

Adopt **Next.js 16+ App Router** as the integrated frontend technology stack with the following components:

**Core Framework:**
- **Framework:** Next.js 16+ (App Router, not Pages Router)
- **Runtime:** React 18+ (Server Components, Suspense, Transitions)
- **Language:** TypeScript 5+ with strict mode enabled
- **Package Manager:** pnpm (fast, efficient, workspace support)

**Styling & UI:**
- **CSS Framework:** Tailwind CSS 3.x (utility-first, responsive design)
- **Component Strategy:** Shadcn/ui components (optional, copy-paste approach)
- **Responsive Design:** Tailwind breakpoints (sm, md, lg, xl)

**Authentication:**
- **Auth Library:** Better Auth (JWT-based, framework-agnostic)
- **Session Management:** HTTP-only cookies for JWT tokens
- **Token Expiration:** 7-day expiration, no refresh tokens in Phase 2

**Data Fetching:**
- **API Client:** Axios with interceptors for JWT headers
- **Server Fetching:** Native `fetch()` in Server Components
- **Client Fetching:** React hooks (`useEffect`) + Axios in Client Components

**Routing Strategy:**
- **Route Groups:** `(auth)` for public routes, `(dashboard)` for protected routes
- **Layouts:** Shared layouts per route group (auth layout, dashboard layout)
- **Middleware:** Next.js middleware for authentication checks on protected routes

**Testing:**
- **Framework:** Jest + React Testing Library
- **Coverage Target:** >80%
- **Test Types:** Component tests, integration tests, E2E (optional with Playwright)

## Consequences

### Positive

- **Integrated Ecosystem:** Next.js + React + Tailwind work seamlessly together with minimal configuration
- **Performance:** Automatic code splitting, image optimization, static generation, ISR
- **Developer Experience:** Fast Refresh, TypeScript integration, excellent error messages
- **SEO-Ready:** Server-side rendering and static generation out of the box
- **Type Safety:** TypeScript strict mode catches errors at compile time
- **Deployment:** Optimized for Vercel with zero-config deployment
- **Component Architecture:** Server Components reduce client bundle size
- **Styling Velocity:** Tailwind enables rapid UI development without CSS files
- **Auth Integration:** Better Auth works natively with Next.js App Router

### Negative

- **Framework Lock-in:** Tightly coupled to Next.js patterns and conventions
- **Learning Curve:** App Router is newer and requires understanding Server vs Client Components
- **Vercel Optimization:** Some features (ISR, Middleware) work best on Vercel platform
- **Build Complexity:** Next.js builds can be slow for large applications
- **Tailwind Verbosity:** Class names can become lengthy for complex components
- **Better Auth Maturity:** Newer library compared to NextAuth/Auth0

## Alternatives Considered

**Alternative A: Remix + styled-components + Cloudflare Pages**
- **Pros:** Better data loading patterns, native form handling, platform-agnostic deployment
- **Cons:** Smaller ecosystem, less mature than Next.js, no native static generation
- **Why Rejected:** Next.js has larger community, better TypeScript support, and better auth library options

**Alternative B: Vite + React + vanilla CSS + AWS Amplify**
- **Pros:** Faster dev server, simpler mental model, complete control
- **Cons:** Manual SSR setup, no framework conventions, more boilerplate
- **Why Rejected:** Too much manual setup for routing, SSR, auth. Next.js provides these out of the box.

**Alternative C: SvelteKit + TailwindCSS + Vercel**
- **Pros:** Smaller bundle sizes, simpler reactivity, less boilerplate
- **Cons:** Smaller ecosystem, fewer React-compatible libraries, team unfamiliarity
- **Why Rejected:** Team has React experience. Better Auth and UI libraries are React-first.

**Alternative D: Next.js Pages Router (instead of App Router)**
- **Pros:** More mature, more tutorials, simpler mental model
- **Cons:** No Server Components, less performant, being phased out by Next.js team
- **Why Rejected:** App Router is the future. Server Components significantly reduce bundle size.

## References

- Feature Spec: `specs/002-phase2-web-app/spec.md`
- Implementation Plan: `specs/002-phase2-web-app/plan.md` (lines 20-30)
- Research: `specs/002-phase2-web-app/research.md` (Next.js App Router Patterns section)
- Related ADRs: ADR-007 (Monorepo Architecture), ADR-010 (Authentication Strategy)
- Evaluator Evidence: `history/prompts/002-phase2-web-app/014-create-adrs-phase2.misc.prompt.md`
