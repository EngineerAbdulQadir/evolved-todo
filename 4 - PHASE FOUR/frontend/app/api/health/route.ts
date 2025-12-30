/**
 * Frontend health check endpoint for Kubernetes deployment (Phase 4 - T009).
 *
 * This endpoint provides health status for the Next.js frontend application
 * and can be used by:
 * - Kubernetes liveness/readiness/startup probes (ADR-001)
 * - Load balancers
 * - Container orchestration platforms
 * - Monitoring tools
 * - Deployment automation
 *
 * Returns:
 *   - HTTP 200: Frontend service is healthy
 *   - JSON response with status, timestamp, service name
 *
 * @ref ADR-001 Containerization Strategy - Health Check Endpoints
 * @ref spec.md FR-003: Health check endpoints required for Kubernetes probes
 */

import { NextResponse } from "next/server";

/**
 * GET /api/health
 *
 * Phase 4 requirements (T009):
 * - Returns JSON with status, timestamp, service name
 * - Returns HTTP 200 for healthy frontend
 * - Responds within 1 second for Kubernetes probe requirements
 *
 * Example response:
 * ```json
 * {
 *   "status": "healthy",
 *   "timestamp": "2025-12-25T20:05:00Z",
 *   "service": "evolved-todo-frontend"
 * }
 * ```
 */
export async function GET() {
  const timestamp = new Date().toISOString();

  return NextResponse.json(
    {
      status: "healthy",
      timestamp,
      service: "evolved-todo-frontend",
      version: process.env.npm_package_version || "1.0.0",
    },
    {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Content-Type": "application/json",
      },
    }
  );
}
