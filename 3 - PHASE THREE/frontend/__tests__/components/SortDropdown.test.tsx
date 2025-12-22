/**
 * Tests for SortDropdown component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SortDropdown, SortOption } from '@/components/tasks/SortDropdown';

describe('SortDropdown Component', () => {
  const mockOnChange = jest.fn();

  const defaultSortOption: SortOption = {
    field: "created_at",
    order: "desc",
    label: "Newest First",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default value', () => {
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    expect(screen.getByText(/Newest First/i)).toBeInTheDocument();
  });

  it('toggles dropdown on button click', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);

    // Dropdown should not be visible initially
    expect(screen.queryByText('Ordering Protocol')).not.toBeInTheDocument();

    // Click to open
    await user.click(button);
    expect(screen.getByText('Ordering Protocol')).toBeInTheDocument();

    // Click to close
    await user.click(button);
    expect(screen.queryByText('Ordering Protocol')).not.toBeInTheDocument();
  });

  it('displays all sort options when opened', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    // Check for all 10 sort options (use getAllByText for "Newest First" which appears in button + dropdown)
    expect(screen.getAllByText('Newest First').length).toBeGreaterThan(0);
    expect(screen.getByText('Oldest First')).toBeInTheDocument();
    expect(screen.getByText('Due Date (Soonest)')).toBeInTheDocument();
    expect(screen.getByText('Due Date (Latest)')).toBeInTheDocument();
    expect(screen.getByText('Priority (High > Low)')).toBeInTheDocument();
    expect(screen.getByText('Priority (Low > High)')).toBeInTheDocument();
    expect(screen.getByText('Title (A-Z)')).toBeInTheDocument();
    expect(screen.getByText('Title (Z-A)')).toBeInTheDocument();
    expect(screen.getByText('Pending First')).toBeInTheDocument();
    expect(screen.getByText('Completed First')).toBeInTheDocument();
  });

  it('highlights currently selected option', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    // Find the option button in dropdown (not the trigger button)
    const dropdownOptions = screen.getAllByRole('button');
    const selectedOption = dropdownOptions.find(opt =>
      opt.textContent?.includes('Newest First') && opt.className.includes('bg-white')
    );

    expect(selectedOption).toHaveClass('bg-white', 'text-black');
  });

  it('calls onChange when a different option is selected', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const oldestFirstOption = screen.getByText('Oldest First');
    await user.click(oldestFirstOption);

    expect(mockOnChange).toHaveBeenCalledWith({
      field: "created_at",
      order: "asc",
      label: "Oldest First",
    });
  });

  it('closes dropdown after selecting an option', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    expect(screen.getByText('Ordering Protocol')).toBeInTheDocument();

    const oldestFirstOption = screen.getByText('Oldest First');
    await user.click(oldestFirstOption);

    // Dropdown should be closed
    expect(screen.queryByText('Ordering Protocol')).not.toBeInTheDocument();
  });

  it('closes dropdown when clicking outside', async () => {
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    fireEvent.click(button);

    expect(screen.getByText('Ordering Protocol')).toBeInTheDocument();

    // Click outside
    fireEvent.mouseDown(document.body);

    expect(screen.queryByText('Ordering Protocol')).not.toBeInTheDocument();
  });

  it('does not close dropdown when clicking inside', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const config = screen.getByText('Ordering Protocol');
    fireEvent.mouseDown(config);

    // Dropdown should still be open
    expect(screen.getByText('Ordering Protocol')).toBeInTheDocument();
  });

  it('updates display when value prop changes', () => {
    const { rerender } = render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    expect(screen.getByText(/Newest First/i)).toBeInTheDocument();

    // Change value
    const newValue: SortOption = {
      field: "priority",
      order: "desc",
      label: "Priority (High > Low)",
    };

    rerender(<SortDropdown value={newValue} onChange={mockOnChange} />);

    expect(screen.getByText(/Priority \(High > Low\)/i)).toBeInTheDocument();
  });

  it('handles due date sorting options', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const dueDateOption = screen.getByText('Due Date (Soonest)');
    await user.click(dueDateOption);

    expect(mockOnChange).toHaveBeenCalledWith({
      field: "due_date",
      order: "asc",
      label: "Due Date (Soonest)",
    });
  });

  it('handles priority sorting options', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const priorityOption = screen.getByText('Priority (Low > High)');
    await user.click(priorityOption);

    expect(mockOnChange).toHaveBeenCalledWith({
      field: "priority",
      order: "asc",
      label: "Priority (Low > High)",
    });
  });

  it('handles title sorting options', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const titleOption = screen.getByText('Title (Z-A)');
    await user.click(titleOption);

    expect(mockOnChange).toHaveBeenCalledWith({
      field: "title",
      order: "desc",
      label: "Title (Z-A)",
    });
  });

  it('handles completion status sorting options', async () => {
    const user = userEvent.setup();
    render(<SortDropdown value={defaultSortOption} onChange={mockOnChange} />);

    const button = screen.getByText(/Newest First/i);
    await user.click(button);

    const completedOption = screen.getByText('Completed First');
    await user.click(completedOption);

    expect(mockOnChange).toHaveBeenCalledWith({
      field: "completed",
      order: "desc",
      label: "Completed First",
    });
  });

  it('shows check icon next to selected option', async () => {
    const user = userEvent.setup();
    const priorityValue: SortOption = {
      field: "priority",
      order: "desc",
      label: "Priority (High > Low)",
    };

    render(<SortDropdown value={priorityValue} onChange={mockOnChange} />);

    const button = screen.getByText(/Priority/i);
    await user.click(button);

    // Find the selected option in dropdown
    const dropdownOptions = screen.getAllByRole('button');
    const selectedOption = dropdownOptions.find(opt =>
      opt.textContent?.includes('Priority (High > Low)') && opt.className.includes('bg-white')
    );

    // Check icon should be present
    expect(selectedOption?.querySelector('svg')).toBeInTheDocument();
  });

  it('falls back to Newest First for unknown sort option', () => {
    const unknownValue: SortOption = {
      field: "created_at" as any,
      order: "unknown" as any,
      label: "Unknown",
    };

    render(<SortDropdown value={unknownValue} onChange={mockOnChange} />);

    // Should show fallback
    expect(screen.getByText(/Newest First/i)).toBeInTheDocument();
  });
});
