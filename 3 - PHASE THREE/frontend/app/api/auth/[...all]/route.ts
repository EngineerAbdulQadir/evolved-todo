/**
 * Better Auth API route handler.
 *
 * This catch-all route handles all authentication requests:
 * - POST /api/auth/sign-up (registration)
 * - POST /api/auth/sign-in (login)
 * - POST /api/auth/sign-out (logout)
 * - GET /api/auth/session (get current session)
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
