/**
 * Tests for DateTimePicker component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DateTimePicker } from '@/components/common/DateTimePicker';

describe('DateTimePicker Component', () => {
  const mockOnDueDateChange = jest.fn();
  const mockOnDueTimeChange = jest.fn();

  const defaultProps = {
    dueDate: null,
    dueTime: null,
    onDueDateChange: mockOnDueDateChange,
    onDueTimeChange: mockOnDueTimeChange,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Date Selection', () => {
    it('renders date input field', () => {
      render(<DateTimePicker {...defaultProps} />);

      expect(screen.getByLabelText(/Execution_Date/i)).toBeInTheDocument();
    });

    it('allows selecting a date', async () => {
      render(<DateTimePicker {...defaultProps} />);

      const dateInput = screen.getByLabelText(/Execution_Date/i);
      fireEvent.change(dateInput, { target: { value: '2025-12-31' } });

      expect(mockOnDueDateChange).toHaveBeenCalledWith('2025-12-31');
    });

    it('displays selected date value', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      const dateInput = screen.getByLabelText(/Execution_Date/i);
      expect(dateInput).toHaveValue('2025-12-31');
    });

    it('shows clear button when date is set', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      expect(screen.getByText(/Clear_Date/i)).toBeInTheDocument();
    });

    it('does not show clear button when no date is set', () => {
      render(<DateTimePicker {...defaultProps} />);

      expect(screen.queryByText(/Clear_Date/i)).not.toBeInTheDocument();
    });

    it('clears date and time when clear button is clicked', async () => {
      const user = userEvent.setup();
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:00" />);

      const clearButton = screen.getByText(/Clear_Date/i);
      await user.click(clearButton);

      expect(mockOnDueDateChange).toHaveBeenCalledWith(null);
      expect(mockOnDueTimeChange).toHaveBeenCalledWith(null);
    });

    it('clears time when date is cleared via input', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:00" />);

      const dateInput = screen.getByLabelText(/Execution_Date/i);
      fireEvent.change(dateInput, { target: { value: '' } });

      expect(mockOnDueDateChange).toHaveBeenCalledWith(null);
      expect(mockOnDueTimeChange).toHaveBeenCalledWith(null);
    });
  });

  describe('Time Selection', () => {
    it('does not show time input when no date is set', () => {
      render(<DateTimePicker {...defaultProps} />);

      expect(screen.queryByLabelText(/Execution_Time/i)).not.toBeInTheDocument();
    });

    it('shows time input when date is set', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      expect(screen.getByLabelText(/Execution_Time/i)).toBeInTheDocument();
    });

    it('allows selecting a time', async () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      const timeInput = screen.getByLabelText(/Execution_Time/i);
      fireEvent.change(timeInput, { target: { value: '14:30' } });

      expect(mockOnDueTimeChange).toHaveBeenCalledWith('14:30');
    });

    it('displays selected time value', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:30" />);

      const timeInput = screen.getByLabelText(/Execution_Time/i);
      expect(timeInput).toHaveValue('14:30');
    });

    it('shows optional timing message when time input is visible', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      expect(screen.getByText(/Optional precision timing/i)).toBeInTheDocument();
    });

    it('clears time when empty value is set', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:00" />);

      const timeInput = screen.getByLabelText(/Execution_Time/i);
      fireEvent.change(timeInput, { target: { value: '' } });

      expect(mockOnDueTimeChange).toHaveBeenCalledWith(null);
    });
  });

  describe('Error Handling', () => {
    it('does not show error message by default', () => {
      render(<DateTimePicker {...defaultProps} />);

      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it('displays error message when error prop is provided', () => {
      render(<DateTimePicker {...defaultProps} error="Invalid date format" />);

      expect(screen.getByText('Invalid date format')).toBeInTheDocument();
    });

    it('shows error icon when error is present', () => {
      const { container } = render(<DateTimePicker {...defaultProps} error="Error message" />);

      const errorSection = screen.getByText('Error message').parentElement;
      expect(errorSection).toHaveClass('text-red-400');
    });
  });

  describe('Integration', () => {
    it('handles complete date-time workflow', async () => {
      const { rerender } = render(<DateTimePicker {...defaultProps} />);

      // Step 1: Select date
      const dateInput = screen.getByLabelText(/Execution_Date/i);
      fireEvent.change(dateInput, { target: { value: '2025-12-31' } });
      expect(mockOnDueDateChange).toHaveBeenCalledWith('2025-12-31');

      // Step 2: Rerender with date set (simulate parent state update)
      rerender(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      // Step 3: Time input should now be visible
      const timeInput = screen.getByLabelText(/Execution_Time/i);
      expect(timeInput).toBeInTheDocument();

      // Step 4: Select time
      fireEvent.change(timeInput, { target: { value: '14:00' } });
      expect(mockOnDueTimeChange).toHaveBeenCalledWith('14:00');

      // Step 5: Rerender with time set
      rerender(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:00" />);

      // Step 6: Clear should clear both
      const user = userEvent.setup();
      const clearButton = screen.getByText(/Clear_Date/i);
      await user.click(clearButton);

      expect(mockOnDueDateChange).toHaveBeenCalledWith(null);
      expect(mockOnDueTimeChange).toHaveBeenCalledWith(null);
    });

    it('maintains date when time is changed', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="10:00" />);

      const timeInput = screen.getByLabelText(/Execution_Time/i);
      fireEvent.change(timeInput, { target: { value: '15:00' } });

      expect(mockOnDueTimeChange).toHaveBeenCalledWith('15:00');
      expect(mockOnDueDateChange).not.toHaveBeenCalled();
    });

    it('shows time input immediately when both date and time are provided', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" dueTime="14:00" />);

      expect(screen.getByLabelText(/Execution_Time/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Execution_Time/i)).toHaveValue('14:00');
    });
  });

  describe('Styling and Accessibility', () => {
    it('has proper labels for screen readers', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      expect(screen.getByLabelText(/Execution_Date/i)).toHaveAttribute('type', 'date');
      expect(screen.getByLabelText(/Execution_Time/i)).toHaveAttribute('type', 'time');
    });

    it('has proper ids for form association', () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      const dateInput = screen.getByLabelText(/Execution_Date/i);
      const timeInput = screen.getByLabelText(/Execution_Time/i);

      expect(dateInput).toHaveAttribute('id', 'due_date');
      expect(timeInput).toHaveAttribute('id', 'due_time');
    });

    it('clear button has proper type to prevent form submission', async () => {
      render(<DateTimePicker {...defaultProps} dueDate="2025-12-31" />);

      const clearButton = screen.getByText(/Clear_Date/i);
      expect(clearButton).toHaveAttribute('type', 'button');
    });
  });
});
