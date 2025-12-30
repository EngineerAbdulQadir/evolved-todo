# Task: T013, T015, T017 - Frontend multi-stage Dockerfile with health checks
# Ref: ADR-001 - Containerization Strategy with Multi-Stage Builds
# Base: node:22-alpine
# Target: <150MB image size (FR-002)
# Security: Run as non-root user UID 1000 (FR-004)

# ============================================
# Stage 1: Dependencies and Build
# ============================================
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files for dependency installation
COPY package.json package-lock.json* ./

# Install ALL dependencies (needed for build)
RUN npm ci && \
    npm cache clean --force

# Copy source code
COPY . .

# Build Next.js application with standalone output
# This creates a minimal .next/standalone folder
ENV NEXT_TELEMETRY_DISABLED=1
# Set placeholder for build-time (actual secret injected at runtime via K8s)
ENV BETTER_AUTH_SECRET=build-time-placeholder-will-be-replaced-at-runtime
ENV BETTER_AUTH_URL=http://localhost:3000
RUN npm run build

# ============================================
# Stage 2: Production Runtime (Standalone)
# ============================================
FROM node:22-alpine AS production

WORKDIR /app

# Use existing node user (already UID 1000 in node:22-alpine)
# Ref: ADR-001 - Non-root containers requirement

# Copy only the standalone server bundle (much smaller than full node_modules)
COPY --from=builder --chown=node:node /app/.next/standalone ./
# Copy static files
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
# Copy public assets
COPY --from=builder --chown=node:node /app/public ./public

# Switch to non-root user (node user is UID 1000)
USER node

# Expose port 3000 for Next.js frontend (T017)
EXPOSE 3000

# Health check endpoint for Kubernetes liveness/readiness probes (T015)
# Ref: ADR-001 - Health check endpoints required for container orchestration
# Interval: 30s, Timeout: 3s, Start period: 40s (Next.js startup), Retries: 3
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start Next.js standalone server (T017)
# Standalone mode has server.js in the root
CMD ["node", "server.js"]
