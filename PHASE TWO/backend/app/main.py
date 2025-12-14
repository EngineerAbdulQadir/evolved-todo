"""
Main FastAPI application entry point with CORS configuration.

This module initializes the FastAPI app, configures middleware,
and sets up routing for the Evolved Todo backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings

app = FastAPI(
    title="Evolved Todo API",
    description="""
    # Evolved Todo Backend API

    Production-ready REST API for task management with multi-user support.

    ## Features

    - **Authentication**: JWT-based authentication with Better Auth
    - **Task Management**: Full CRUD operations for tasks
    - **Advanced Filtering**: Search, sort, and filter tasks by multiple criteria
    - **Due Dates & Reminders**: Track task deadlines with visual indicators
    - **Recurring Tasks**: Automatic task creation for daily, weekly, monthly patterns
    - **Priorities & Tags**: Organize tasks with priorities and custom tags
    - **Multi-User**: Complete data isolation between users

    ## Rate Limiting

    - **Limit**: 100 requests per minute per user
    - **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
    - **Status**: 429 when limit exceeded

    ## Authentication

    Most endpoints require authentication via JWT token in the Authorization header:

    ```
    Authorization: Bearer <jwt_token>
    ```

    Get a token by calling `/api/auth/login` or `/api/auth/register`.

    ## Error Responses

    All errors follow this format:

    ```json
    {
      "detail": "Error message",
      "status_code": 400
    }
    ```

    Common status codes:
    - `200`: Success
    - `201`: Created
    - `400`: Bad Request
    - `401`: Unauthorized
    - `403`: Forbidden
    - `404`: Not Found
    - `429`: Rate Limit Exceeded
    - `500`: Internal Server Error
    """,
    version="2.0.0",
    debug=settings.debug,
    contact={
        "name": "Evolved Todo Support",
        "url": "https://github.com/yourusername/evolved-todo",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc
    openapi_url="/api/openapi.json",  # OpenAPI schema
)

# Configure CORS for frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add rate limiting middleware (T225)
from app.middleware.rate_limit import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)

# Register API routers
from app.api import auth, tasks, health

app.include_router(auth.router, prefix="/api/auth")
app.include_router(tasks.router, prefix="/api")
app.include_router(health.router, prefix="/api")  # Health check at root level


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint for health check."""
    return {"message": "Evolved Todo API is running", "version": "2.0.0"}


# Global exception handlers
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a generic 500 response.
    """
    # In production, log to monitoring service (e.g., Sentry)
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )
