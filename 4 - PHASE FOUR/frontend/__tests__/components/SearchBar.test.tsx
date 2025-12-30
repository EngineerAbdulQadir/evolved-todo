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

  it('calls onChange for each character typed', async () => {
    const user = userEvent.setup({ delay: null });
    render(<SearchBar value="" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    await user.type(input, 'test');

    // Component calls onChange immediately for each character (no debouncing)
    expect(mockOnChange).toHaveBeenCalled();
    // Should be called once per character
    expect(mockOnChange).toHaveBeenCalledTimes(4);
  });

  it('syncs with external value changes', () => {
    const { rerender } = render(<SearchBar value="initial" onChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('SEARCH_DATABASE...');
    expect(input).toHaveValue('initial');

    // External value change
    rerender(<SearchBar value="updated" onChange={mockOnChange} />);

    expect(input).toHaveValue('updated');
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
});
