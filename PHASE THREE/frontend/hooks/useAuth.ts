/**
 * Authentication hook for managing user state and auth operations.
 *
 * This hook provides a simple interface for authentication throughout
 * the application using FastAPI backend.
 */

"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import * as authApi from "@/lib/api/auth";

interface RegisterData {
  email: string;
  password: string;
  name?: string;
}

interface LoginData {
  email: string;
  password: string;
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<authApi.User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);

  // Initialize user from localStorage on mount
  useEffect(() => {
    const token = authApi.getAuthToken();
    const storedUser = authApi.getUser();

    if (token && storedUser) {
      setUser(storedUser);

      // Optionally validate token with backend
      authApi.getMe()
        .then((currentUser) => {
          setUser(currentUser);
        })
        .catch(() => {
          // Token invalid, clear auth
          authApi.removeAuthToken();
          setUser(null);
        })
        .finally(() => {
          setInitializing(false);
        });
    } else {
      setInitializing(false);
    }
  }, []);

  const register = async (data: RegisterData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authApi.register(data);
      setUser(response.user);

      // Redirect to dashboard on success
      router.push("/dashboard");
      return { success: true };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed";
      setError(message);
      console.error("Registration error:", message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const login = async (data: LoginData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authApi.login(data);
      setUser(response.user);

      // Redirect to dashboard on success
      router.push("/dashboard");
      return { success: true };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      console.error("Login error:", message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    setError(null);

    try {
      authApi.logout();
      setUser(null);
      router.push("/");
      return { success: true };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Logout failed";
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    session: user ? { user } : null,
    isAuthenticated: !!user,
    isLoading: initializing || loading,
    error,
    register,
    login,
    logout,
  };
}
