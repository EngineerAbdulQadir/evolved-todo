/**
 * Mock API utilities for testing
 */

import { Task, TaskCreate, TaskUpdate } from '@/types/task';

export const mockTask: Task = {
  id: 1,
  user_id: 'test-user-id',
  title: 'Test Task',
  description: 'Test Description',
  is_complete: false,
  created_at: '2025-12-10T00:00:00Z',
  updated_at: '2025-12-10T00:00:00Z',
  completed_at: null,
  priority: 'medium',
  tags: ['test'],
  due_date: null,
  due_time: null,
  recurrence: null,
  recurrence_day: null,
};

export const mockTasks: Task[] = [
  mockTask,
  {
    ...mockTask,
    id: 2,
    title: 'Second Task',
    priority: 'high',
    is_complete: true,
    completed_at: '2025-12-11T00:00:00Z',
  },
  {
    ...mockTask,
    id: 3,
    title: 'Third Task',
    priority: 'low',
    tags: ['work', 'urgent'],
  },
];

export const mockTaskCreate: TaskCreate = {
  title: 'New Task',
  description: 'New Description',
  priority: 'medium',
  tags: [],
};

export const mockTaskUpdate: TaskUpdate = {
  title: 'Updated Task',
  description: 'Updated Description',
};

/**
 * Mock fetch responses
 */
export const mockFetchSuccess = <T>(data: T) => {
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve(data),
    status: 200,
  } as Response);
};

export const mockFetchError = (status: number, message: string) => {
  return Promise.resolve({
    ok: false,
    json: () => Promise.resolve({ detail: message }),
    status,
  } as Response);
};

/**
 * Mock API client
 */
export const createMockApiClient = () => {
  return {
    getTasks: jest.fn(() => Promise.resolve({ tasks: mockTasks, total: mockTasks.length })),
    createTask: jest.fn((data: TaskCreate) =>
      Promise.resolve({ ...mockTask, ...data, id: 4 })
    ),
    updateTask: jest.fn((id: number, data: TaskUpdate) =>
      Promise.resolve({ ...mockTask, id, ...data })
    ),
    deleteTask: jest.fn(() => Promise.resolve()),
    toggleTaskComplete: jest.fn((id: number) =>
      Promise.resolve({ ...mockTask, id, is_complete: true })
    ),
  };
};
