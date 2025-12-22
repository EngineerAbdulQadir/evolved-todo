/**
 * Task type definitions matching backend schemas.
 */

export type Priority = "high" | "medium" | "low";
export type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  is_complete: boolean;
  created_at: string;
  completed_at: string | null;
  priority: Priority | null;
  tags: string[];
  due_date: string | null;
  due_time: string | null;
  recurrence: RecurrencePattern | null;
  recurrence_day: number | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string;
  due_time?: string;
  recurrence?: RecurrencePattern;
  recurrence_day?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
  tags?: string[];
  due_date?: string;
  due_time?: string;
  recurrence?: RecurrencePattern;
  recurrence_day?: number;
  is_complete?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}
