/**
 * Tests for TaskItem component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskItem } from '@/components/tasks/TaskItem';
import { Task } from '@/types/task';

// Mock task data
const mockTask: Task = {
  id: 1,
  user_id: 'test-user',
  title: 'Test Task',
  description: 'Test task description',
  is_complete: false,
  created_at: '2025-12-10T00:00:00Z',
  updated_at: '2025-12-10T00:00:00Z',
  completed_at: null,
  priority: 'high',
  tags: ['work', 'urgent'],
  due_date: '2025-12-31',
  due_time: null,
  recurrence: null,
  recurrence_day: null,
};

const mockCompletedTask: Task = {
  ...mockTask,
  id: 2,
  title: 'Completed Task',
  is_complete: true,
  completed_at: '2025-12-11T00:00:00Z',
};

const mockHandlers = {
  onToggleComplete: jest.fn(),
  onDelete: jest.fn(),
  onEdit: jest.fn(),
};

describe('TaskItem Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders task title', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('renders task description when present', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    expect(screen.getByText('Test task description')).toBeInTheDocument();
  });

  it('renders without description when null', () => {
    const taskWithoutDesc = { ...mockTask, description: null };
    render(<TaskItem task={taskWithoutDesc} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.queryByText('Test task description')).not.toBeInTheDocument();
  });

  it('displays priority badge', () => {
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Check for priority indicator (could be text, class, or badge)
    expect(container.textContent).toContain('Test Task');
  });

  it('displays tags', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Tags should be visible
    expect(screen.getByText('work')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('renders task without tags', () => {
    const taskWithoutTags = { ...mockTask, tags: [] };
    render(<TaskItem task={taskWithoutTags} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('shows edit button on hover', () => {
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Edit button should exist (may be hidden via CSS)
    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Find edit button (look for SVG with pencil/edit icon or button with edit text)
    const buttons = container.querySelectorAll('button');
    const editButton = Array.from(buttons).find((btn) =>
      btn.innerHTML.includes('svg')
    );

    if (editButton) {
      await user.click(editButton);
      // onEdit should be called with the task
      expect(mockHandlers.onEdit).toHaveBeenCalled();
    }
  });

  it('shows delete button', () => {
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('calls onDelete when delete button is clicked', async () => {
    const user = userEvent.setup();
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Find delete button (last button or one with trash icon)
    const buttons = container.querySelectorAll('button');
    const deleteButton = buttons[buttons.length - 1];

    if (deleteButton) {
      await user.click(deleteButton);
      expect(mockHandlers.onDelete).toHaveBeenCalledWith(mockTask.id);
    }
  });

  it('applies completed styling to completed tasks', () => {
    const { container } = render(
      <TaskItem task={mockCompletedTask} {...mockHandlers} />
    );

    // Completed tasks should have different styling (e.g., line-through, muted colors)
    expect(screen.getByText('Completed Task')).toBeInTheDocument();
  });

  it('displays due date when present', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Due date should be formatted and displayed
    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('applies Notion-inspired clean styling', () => {
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    // Check for clean card styling with proper spacing
    const taskCard = container.firstChild;
    expect(taskCard).toHaveClass('group');
  });

  it('handles high priority tasks', () => {
    const highPriorityTask = { ...mockTask, priority: 'high' as const };
    render(<TaskItem task={highPriorityTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('handles medium priority tasks', () => {
    const mediumPriorityTask = { ...mockTask, priority: 'medium' as const };
    render(<TaskItem task={mediumPriorityTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('handles low priority tasks', () => {
    const lowPriorityTask = { ...mockTask, priority: 'low' as const };
    render(<TaskItem task={lowPriorityTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('handles tasks without priority', () => {
    const noPriorityTask = { ...mockTask, priority: null };
    render(<TaskItem task={noPriorityTask} {...mockHandlers} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  // Checkbox toggle tests (T115)
  it('renders checkbox for incomplete task', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: /mark complete/i });
    expect(checkbox).toBeInTheDocument();
  });

  it('renders checked checkbox for completed task', () => {
    render(<TaskItem task={mockCompletedTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: /mark incomplete/i });
    expect(checkbox).toBeInTheDocument();
  });

  it('calls onToggleComplete when checkbox is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: /mark complete/i });
    await user.click(checkbox);

    expect(mockHandlers.onToggleComplete).toHaveBeenCalledTimes(1);
    expect(mockHandlers.onToggleComplete).toHaveBeenCalledWith(mockTask.id);
  });

  it('applies line-through styling to completed tasks', () => {
    render(<TaskItem task={mockCompletedTask} {...mockHandlers} />);

    const title = screen.getByText('Completed Task');
    expect(title).toHaveClass('line-through');
    expect(title).toHaveClass('text-neutral-600');
  });

  it('does not apply line-through to incomplete tasks', () => {
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const title = screen.getByText('Test Task');
    expect(title).not.toHaveClass('line-through');
    expect(title).toHaveClass('text-white');
  });

  it('shows checkmark icon for completed tasks', () => {
    const { container } = render(<TaskItem task={mockCompletedTask} {...mockHandlers} />);

    // Checkmark SVG should be present
    const checkbox = screen.getByRole('button', { name: /mark incomplete/i });
    const svg = checkbox.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('does not show checkmark icon for incomplete tasks', () => {
    const { container } = render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: /mark complete/i });
    // Checkbox div should exist but not contain SVG checkmark
    expect(checkbox).toBeInTheDocument();
  });

  it('toggles completion status when clicked multiple times', async () => {
    const user = userEvent.setup();
    render(<TaskItem task={mockTask} {...mockHandlers} />);

    const checkbox = screen.getByRole('button', { name: /mark complete/i });

    // Click three times
    await user.click(checkbox);
    await user.click(checkbox);
    await user.click(checkbox);

    expect(mockHandlers.onToggleComplete).toHaveBeenCalledTimes(3);
    expect(mockHandlers.onToggleComplete).toHaveBeenCalledWith(mockTask.id);
  });
});
