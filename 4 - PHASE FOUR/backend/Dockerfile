# Task: T014, T016, T018 - Backend multi-stage Dockerfile with health checks
# Ref: ADR-001 - Containerization Strategy with Multi-Stage Builds
# Base: python:3.13-slim
# Target: <200MB image size (FR-002)
# Security: Run as non-root user UID 1000 (FR-004)

# ============================================
# Stage 1: Dependencies Installation
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Copy dependency specification files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
# Use --no-cache-dir to reduce layer size
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir \
    fastapi uvicorn[standard] sqlmodel asyncpg alembic \
    pydantic pydantic-settings python-jose[cryptography] \
    passlib[bcrypt] python-multipart email-validator \
    "bcrypt<5.0" openai mcp openai-chatkit sse-starlette && \
    # Remove unnecessary files to reduce size
    find /app/.venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type d -name "*.dist-info" -exec rm -rf {}/RECORD {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete && \
    find /app/.venv -type f -name "*.pyo" -delete

# ============================================
# Stage 2: Production Runtime
# ============================================
FROM python:3.13-slim AS production

WORKDIR /app

# Install only curl for health checks, then clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root user for security (UID 1000)
# Ref: ADR-001 - Non-root containers requirement
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/sh -m appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appgroup ./app /app/app

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port 8000 for FastAPI backend (T018)
EXPOSE 8000

# Health check endpoint for Kubernetes liveness/readiness probes (T016)
# Ref: ADR-001 - Health check endpoints required for container orchestration
# Interval: 30s, Timeout: 3s, Start period: 40s (DB connection), Retries: 3
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI server with Uvicorn (T018)
# Ref: Phase 3 main.py - FastAPI application entry point
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
