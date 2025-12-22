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
    const filterButton = screen.getByText('Filters');
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
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.getByText('Any Priority')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
    expect(screen.getByText('low')).toBeInTheDocument();
  });

  it('renders tag filter buttons', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Click to open dropdown
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.getByText('work')).toBeInTheDocument();
    expect(screen.getByText('personal')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('calls onStatusChange when status button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    await user.click(activeButton);

    expect(mockHandlers.onStatusChange).toHaveBeenCalledWith('active');
  });

  it('calls onPriorityChange when priority button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const highButton = screen.getByText('high');
    await user.click(highButton);

    expect(mockHandlers.onPriorityChange).toHaveBeenCalledWith('high');
  });

  it('calls onTagToggle when tag button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    await user.click(workTag);

    expect(mockHandlers.onTagToggle).toHaveBeenCalledWith('work');
  });

  it('highlights active status filter', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    expect(activeButton).toHaveClass('bg-white', 'text-black');
  });

  it('highlights active priority filter', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} priorityFilter="high" />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const highButton = screen.getByText('high');
    expect(highButton).toHaveClass('bg-white', 'text-black');
  });

  it('highlights selected tags', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} selectedTags={['work', 'urgent']} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    expect(workTag).toHaveClass('bg-white', 'text-black');
  });

  it('shows clear filters button when filters are active', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.getByText('Clear')).toBeInTheDocument();
  });

  it('does not show clear filters button when no filters are active', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.queryByText('Clear')).not.toBeInTheDocument();
  });

  it('calls onClearFilters when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} statusFilter="active" />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const clearButton = screen.getByText('Clear');
    await user.click(clearButton);

    expect(mockHandlers.onClearFilters).toHaveBeenCalled();
  });

  it('shows clear button when priority filter is set', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} priorityFilter="high" />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.getByText('Clear')).toBeInTheDocument();
  });

  it('shows clear button when tags are selected', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} selectedTags={['work']} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    expect(screen.getByText('Clear')).toBeInTheDocument();
  });

  it('does not render tag section when no tags available', () => {
    render(<TaskFilters {...defaultProps} availableTags={[]} />);

    // Open dropdown first
    const filterButton = screen.getByText('Filters');
    fireEvent.click(filterButton);

    // Tag section should not exist (no Tags label)
    expect(screen.queryByText('Tags')).not.toBeInTheDocument();
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
    const filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const activeButton = screen.getByText('active');
    const highButton = screen.getByText('high');

    expect(activeButton).toHaveClass('bg-white');
    expect(highButton).toHaveClass('bg-white');
  });

  it('supports toggling tags on and off', async () => {
    const user = userEvent.setup();
    const { rerender } = render(<TaskFilters {...defaultProps} />);

    // Open dropdown first
    let filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const workTag = screen.getByText('work');
    await user.click(workTag);

    expect(mockHandlers.onTagToggle).toHaveBeenCalledWith('work');

    // Close dropdown after click
    await user.click(filterButton);

    // Simulate tag being selected
    rerender(<TaskFilters {...defaultProps} selectedTags={['work']} />);

    // Open dropdown again after rerender to verify selected state
    filterButton = screen.getByText('Filters');
    await user.click(filterButton);

    const workTagSelected = screen.getByText('work');
    expect(workTagSelected).toHaveClass('bg-white');
  });

  it('shows active filter count in badge', () => {
    render(<TaskFilters {...defaultProps} statusFilter="active" priorityFilter="high" selectedTags={['work']} />);

    // Badge should show count of 3 active filters
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('toggles dropdown visibility on button click', async () => {
    const user = userEvent.setup();
    render(<TaskFilters {...defaultProps} />);

    const filterButton = screen.getByText('Filters');

    // Dropdown should not be visible initially
    expect(screen.queryByText('System Filters')).not.toBeInTheDocument();

    // Click to open
    await user.click(filterButton);
    expect(screen.getByText('System Filters')).toBeInTheDocument();

    // Click to close
    await user.click(filterButton);
    expect(screen.queryByText('System Filters')).not.toBeInTheDocument();
  });
});
