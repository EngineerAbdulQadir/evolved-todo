/**
 * Tests for TaskFilters component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskFilters } from '@/components/tasks/TaskFilters';

describe('TaskFilters Component', () => {
  const mockHandlers = {
    onStatusChange: jest.fn(),
    onPriorityChange: jest.fn(),
    onTagToggle: jest.fn(),
    onClearFilters: jest.fn(),
  };

  const defaultProps = {
    statusFilter: 'all' as const,
    priorityFilter: 'all' as const,
    selectedTags: [],
    availableTags: ['work', 'personal', 'urgent'],
    ...mockHandlers,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders status filter buttons', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Click to open dropdown
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    // Check for status buttons (lowercase in component)
    expect(screen.getByText('all')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('renders priority filter buttons', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Click to open dropdown
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.getByText('ALL LEVELS')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
    expect(screen.getByText('low')).toBeInTheDocument();
  });

  it('renders tag filter buttons', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Click to open dropdown
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.getByText('work')).toBeInTheDocument();
    expect(screen.getByText('personal')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('calls onStatusChange when status button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    await user.click(activeButton);

    expect(mockHandlers.onStatusChange).toHaveBeenCalledWith('active');
  });

  it('calls onPriorityChange when priority button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const highButton = screen.getByText('high');
    await user.click(highButton);

    expect(mockHandlers.onPriorityChange).toHaveBeenCalledWith('high');
  });

  it('calls onTagToggle when tag button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    await user.click(workTag);

    expect(mockHandlers.onTagToggle).toHaveBeenCalledWith('work');
  });

  it('highlights active status filter', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    expect(activeButton).toHaveClass('bg-cyan-950/50', 'border-cyan-500', 'text-cyan-400');
  });

  it('highlights active priority filter', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} priorityFilter="high" />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const highButton = screen.getByText('high');
    expect(highButton).toHaveClass('bg-red-950/50', 'border-red-500', 'text-red-400');
  });

  it('highlights selected tags', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} selectedTags={['work', 'urgent']} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    expect(workTag).toHaveClass('bg-purple-950/50', 'border-purple-500', 'text-purple-300');
  });

  it('shows clear filters button when filters are active', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('does not show clear filters button when no filters are active', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.queryByText('Reset')).not.toBeInTheDocument();
  });

  it('calls onClearFilters when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const clearButton = screen.getByText('Reset');
    await user.click(clearButton);

    expect(mockHandlers.onClearFilters).toHaveBeenCalled();
  });

  it('shows clear button when priority filter is set', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} priorityFilter="high" />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('shows clear button when tags are selected', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} selectedTags={['work']} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('does not render tag section when no tags available', () => {
    render(<TaskFilters {...defaultProps} availableTags={[]} />);

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    fireEvent.click(filterButton);

    // Tag section should not exist
    expect(screen.queryByText('Filter_Tags')).not.toBeInTheDocument();
  });

  it('handles multiple filter selections', async () => {
    const user = userEvent.setup();
    render(
      <TaskFilters
        {...defaultProps}
        statusFilter="active"
        priorityFilter="high"
      />
    );

    // Open dropdown first
    const filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    const highButton = screen.getByText('high');

    expect(activeButton).toHaveClass('bg-cyan-950/50');
    expect(highButton).toHaveClass('bg-red-950/50');
  });

  it('supports toggling tags on and off', async () => {
    const user = userEvent.setup();
    const { rerender } = render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    let filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    await user.click(workTag);

    expect(mockHandlers.onTagToggle).toHaveBeenCalledWith('work');

    // Close dropdown after click
    await user.click(filterButton);

    // Simulate tag being selected
    rerender(<TaskFilters {...defaultProps} selectedTags={['work']} />);

    // Open dropdown again after rerender to verify selected state
    filterButton = screen.getByText('FILTERS');
    await user.click(filterButton);

    const workTagSelected = screen.getByText('work');
    expect(workTagSelected).toHaveClass('bg-purple-950/50');
  });

  it('shows active filter count in badge', () => {
    render(<TaskFilters {...defaultProps} statusFilter="active" priorityFilter="high" selectedTags={['work']} />);

    // Badge should show count of 3 active filters
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('toggles dropdown visibility on button click', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    const filterButton = screen.getByText('FILTERS');

    // Dropdown should not be visible initially
    expect(screen.queryByText('Configure View')).not.toBeInTheDocument();

    // Click to open
    await user.click(filterButton);
    expect(screen.getByText('Configure View')).toBeInTheDocument();

    // Click to close
    await user.click(filterButton);
    expect(screen.queryByText('Configure View')).not.toBeInTheDocument();
  });
});
