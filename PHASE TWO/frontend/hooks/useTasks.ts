/**
 * Custom hook for task management operations.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import type { Task, TaskCreate, TaskUpdate } from "@/types/task";
import {
  getTasks,
  createTask as apiCreateTask,
  updateTask as apiUpdateTask,
  deleteTask as apiDeleteTask,
  toggleTaskComplete as apiToggleTaskComplete,
  type TaskFilters,
} from "@/lib/api/tasks";

interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  createTask: (taskData: TaskCreate) => Promise<void>;
  updateTask: (taskId: number, taskData: TaskUpdate) => Promise<void>;
  deleteTask: (taskId: number) => Promise<void>;
  toggleComplete: (taskId: number) => Promise<void>;
}

interface UseTasksParams {
  userId: string | null;
  filters?: TaskFilters;
}

export function useTasks(params: UseTasksParams | string | null): UseTasksReturn {
  // Support both old API (userId string) and new API (params object) for backward compatibility
  const userId = typeof params === "string" || params === null ? params : params.userId;
  const filters = typeof params === "object" && params !== null ? params.filters : undefined;

  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    if (!userId) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const response = await getTasks(userId, filters);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }, [userId, filters]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = useCallback(
    async (taskData: TaskCreate) => {
      if (!userId) return;

      try {
        setError(null);
        const newTask = await apiCreateTask(userId, taskData);
        setTasks((prev) => [newTask, ...prev]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to create task");
        throw err;
      }
    },
    [userId]
  );

  const updateTask = useCallback(
    async (taskId: number, taskData: TaskUpdate) => {
      if (!userId) return;

      try {
        setError(null);
        const updatedTask = await apiUpdateTask(userId, taskId, taskData);
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? updatedTask : task))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to update task");
        throw err;
      }
    },
    [userId]
  );

  const deleteTask = useCallback(
    async (taskId: number) => {
      if (!userId) return;

      try {
        setError(null);

        // Optimistically remove task from UI
        const previousTasks = tasks;
        setTasks((prev) => prev.filter((task) => task.id !== taskId));

        try {
          // Call API to delete task
          await apiDeleteTask(userId, taskId);
        } catch (apiError) {
          // Rollback optimistic update on failure
          setTasks(previousTasks);
          throw apiError;
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete task");
        throw err;
      }
    },
    [userId, tasks]
  );

  const toggleComplete = useCallback(
    async (taskId: number) => {
      if (!userId) return;

      try {
        setError(null);

        // Set loading state to prevent multiple clicks
        setIsLoading(true);

        // Call API first (no optimistic update to avoid race conditions)
        await apiToggleTaskComplete(userId, taskId);

        // Refetch to get fresh data from server
        // This ensures we get the correct state, including any recurring task instances
        await fetchTasks();
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to toggle task completion"
        );
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, fetchTasks]
  );

  return {
    tasks,
    isLoading,
    error,
    refetch: fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  };
}
