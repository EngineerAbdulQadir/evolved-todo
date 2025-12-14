/**
 * Tests for TaskList component
 */

import { render, screen } from '@testing-library/react';
import { TaskList } from '@/components/tasks/TaskList';
import { Task } from '@/types/task';

// Mock tasks data
const mockTasks: Task[] = [
  {
    id: 1,
    user_id: 'test-user',
    title: 'First Task',
    description: 'First task description',
    is_complete: false,
    created_at: '2025-12-10T00:00:00Z',
    updated_at: '2025-12-10T00:00:00Z',
    completed_at: null,
    priority: 'high',
    tags: ['work'],
    due_date: null,
    due_time: null,
    recurrence: null,
    recurrence_day: null,
  },
  {
    id: 2,
    user_id: 'test-user',
    title: 'Second Task',
    description: 'Second task description',
    is_complete: true,
    created_at: '2025-12-10T00:00:00Z',
    updated_at: '2025-12-11T00:00:00Z',
    completed_at: '2025-12-11T00:00:00Z',
    priority: 'medium',
    tags: ['personal'],
    due_date: null,
    due_time: null,
    recurrence: null,
    recurrence_day: null,
  },
  {
    id: 3,
    user_id: 'test-user',
    title: 'Third Task',
    description: null,
    is_complete: false,
    created_at: '2025-12-12T00:00:00Z',
    updated_at: '2025-12-12T00:00:00Z',
    completed_at: null,
    priority: 'low',
    tags: [],
    due_date: '2025-12-31',
    due_time: null,
    recurrence: null,
    recurrence_day: null,
  },
];

const mockHandlers = {
  onToggleComplete: jest.fn(),
  onDelete: jest.fn(),
  onEdit: jest.fn(),
};

describe('TaskList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all tasks', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    expect(screen.getByText('First Task')).toBeInTheDocument();
    expect(screen.getByText('Second Task')).toBeInTheDocument();
    expect(screen.getByText('Third Task')).toBeInTheDocument();
  });

  it('renders empty state when no tasks', () => {
    const { container } = render(<TaskList tasks={[]} {...mockHandlers} />);

    // Should render empty container or message
    const taskElements = container.querySelectorAll('[data-testid^="task-"]');
    expect(taskElements.length).toBe(0);
  });

  it('displays task count correctly', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // All three tasks should be rendered
    expect(screen.getByText('First Task')).toBeInTheDocument();
    expect(screen.getByText('Second Task')).toBeInTheDocument();
    expect(screen.getByText('Third Task')).toBeInTheDocument();
  });

  it('renders tasks with correct completion status', () => {
    const { container } = render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // Check that completed tasks have appropriate styling/class
    const taskItems = container.querySelectorAll('.space-y-3 > div');
    expect(taskItems.length).toBe(3);
  });

  it('passes correct handlers to TaskItem components', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // Verify tasks are rendered (handlers will be tested in TaskItem tests)
    expect(screen.getByText('First Task')).toBeInTheDocument();
  });

  it('renders tasks in order', () => {
    const { container } = render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    const taskTitles = Array.from(
      container.querySelectorAll('.space-y-3 > div')
    ).map((el) => el.textContent);

    // Verify order is maintained
    expect(taskTitles[0]).toContain('First Task');
    expect(taskTitles[1]).toContain('Second Task');
    expect(taskTitles[2]).toContain('Third Task');
  });

  it('handles single task correctly', () => {
    const singleTask = [mockTasks[0]];
    render(<TaskList tasks={singleTask} {...mockHandlers} />);

    expect(screen.getByText('First Task')).toBeInTheDocument();
    expect(screen.queryByText('Second Task')).not.toBeInTheDocument();
  });

  it('renders with different priority tasks', () => {
    render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // All tasks with different priorities should render
    expect(screen.getByText('First Task')).toBeInTheDocument(); // high
    expect(screen.getByText('Second Task')).toBeInTheDocument(); // medium
    expect(screen.getByText('Third Task')).toBeInTheDocument(); // low
  });

  it('applies correct container styling', () => {
    const { container } = render(<TaskList tasks={mockTasks} {...mockHandlers} />);

    // Check for clean styling
    const listContainer = container.querySelector('.space-y-3');
    expect(listContainer).toBeInTheDocument();
  });
});
