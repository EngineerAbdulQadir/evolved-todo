/**
 * Tests for SearchBar component
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchBar } from '@/components/tasks/SearchBar';

describe('SearchBar Component', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders with default placeholder', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    expect(input).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    render(<SearchBar value="" onChange={mockOnChange} placeholder="Custom search..." />);

    const input = screen.getByPlaceholderText('Custom search...');
    expect(input).toBeInTheDocument();
  });

  it('displays initial value', () => {
    render(<SearchBar value="initial search" onChange={mockOnChange} />);

    const input = screen.getByDisplayValue('initial search');
    expect(input).toBeInTheDocument();
  });

  it('updates local value on input change', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    await user.type(input, 'test query');

    expect(input).toHaveValue('test query');
  });

  it('debounces onChange calls', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');

    // Type quickly without waiting
    await user.type(input, 'test');

    // onChange should not be called yet
    expect(mockOnChange).not.toHaveBeenCalled();

    // Fast-forward time past debounce delay (300ms)
    jest.advanceTimersByTime(300);

    // Now onChange should be called once with final value
    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('test');
    });
  });

  it('shows clear button when value is present', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    // Initially no clear button
    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();

    // Type something
    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    await user.type(input, 'test');

    // Clear button should appear
    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('clears value when clear button is clicked', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="test value" onChange={mockOnChange} />);

    const clearButton = screen.getByLabelText('Clear search');
    await user.click(clearButton);

    // Input should be cleared
    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    expect(input).toHaveValue('');

    // onChange should be called immediately with empty string
    expect(mockOnChange).toHaveBeenCalledWith('');
  });

  it('syncs with external value changes', () => {
    const { rerender } = render(<SearchBar value="initial" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    expect(input).toHaveValue('initial');

    // External value change
    rerender(<SearchBar value="updated" onChange={mockOnChange} />);

    expect(input).toHaveValue('updated');
  });

  it('hides clear button when value is empty', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);

    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();
  });

  it('maintains focus during input', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    await user.click(input);

    expect(input).toHaveFocus();

    await user.type(input, 'test');

    expect(input).toHaveFocus();
  });

  it('debounces multiple rapid changes correctly', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');

    // Type multiple characters quickly
    await user.type(input, 'a');
    jest.advanceTimersByTime(100);

    await user.type(input, 'b');
    jest.advanceTimersByTime(100);

    await user.type(input, 'c');

    // Should still not have called onChange
    expect(mockOnChange).not.toHaveBeenCalled();

    // Now wait for full debounce
    jest.advanceTimersByTime(300);

    // Should only call once with final value
    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledTimes(1);
      expect(mockOnChange).toHaveBeenCalledWith('abc');
    });
  });

  it('cleans up debounce timer on unmount', () => {
    const { unmount } = render(<SearchBar value="" onChange={mockOnChange} />);

    // Unmount before debounce fires
    unmount();

    // Fast-forward timers
    jest.advanceTimersByTime(300);

    // onChange should not be called
    expect(mockOnChange).not.toHaveBeenCalled();
  });
});
