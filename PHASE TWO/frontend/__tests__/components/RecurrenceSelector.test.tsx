/**
 * Tests for RecurrenceSelector component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RecurrenceSelector } from '@/components/tasks/RecurrenceSelector';

describe('RecurrenceSelector Component', () => {
  const mockOnRecurrenceChange = jest.fn();
  const mockOnRecurrenceDayChange = jest.fn();

  const defaultProps = {
    recurrence: null as null | "none" | "daily" | "weekly" | "monthly",
    recurrenceDay: null as number | null,
    onRecurrenceChange: mockOnRecurrenceChange,
    onRecurrenceDayChange: mockOnRecurrenceDayChange,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default "none" value', () => {
    render(<RecurrenceSelector {...defaultProps} />);

    const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
    expect(recurrenceSelect).toHaveValue('none');
    expect(screen.getByText('NO REPEAT (ONE-TIME)')).toBeInTheDocument();
  });

  it('displays all recurrence options', () => {
    render(<RecurrenceSelector {...defaultProps} />);

    expect(screen.getByText('NO REPEAT (ONE-TIME)')).toBeInTheDocument();
    expect(screen.getByText('DAILY CYCLE')).toBeInTheDocument();
    expect(screen.getByText('WEEKLY CYCLE')).toBeInTheDocument();
    expect(screen.getByText('MONTHLY CYCLE')).toBeInTheDocument();
  });

  describe('Daily Recurrence', () => {
    it('selects daily recurrence', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'daily');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith('daily');
    });

    it('shows daily recurrence info text', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="daily" />);

      expect(screen.getByText(/TASK WILL REGENERATE T\+24H UPON COMPLETION/i)).toBeInTheDocument();
    });

    it('does not show day selector for daily recurrence', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="daily" />);

      expect(screen.queryByLabelText(/Select_Weekday/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Day_Of_Month/i)).not.toBeInTheDocument();
    });
  });

  describe('Weekly Recurrence', () => {
    it('selects weekly recurrence', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'weekly');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith('weekly');
    });

    it('shows weekday selector for weekly recurrence', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      expect(screen.getByLabelText(/Select_Weekday/i)).toBeInTheDocument();
    });

    it('displays all weekday options', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      expect(screen.getByText('MONDAY')).toBeInTheDocument();
      expect(screen.getByText('TUESDAY')).toBeInTheDocument();
      expect(screen.getByText('WEDNESDAY')).toBeInTheDocument();
      expect(screen.getByText('THURSDAY')).toBeInTheDocument();
      expect(screen.getByText('FRIDAY')).toBeInTheDocument();
      expect(screen.getByText('SATURDAY')).toBeInTheDocument();
      expect(screen.getByText('SUNDAY')).toBeInTheDocument();
    });

    it('selects a specific weekday', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      const weekdaySelect = screen.getByLabelText(/Select_Weekday/i);
      await user.selectOptions(weekdaySelect, '1'); // Monday

      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(1);
    });

    it('shows info text when weekday is selected', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" recurrenceDay={1} />);

      expect(screen.getByText(/RECURS EVERY MONDAY/i)).toBeInTheDocument();
    });

    it('shows waiting message when no weekday selected', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      expect(screen.getByText(/WAITING FOR DAY SELECTION/i)).toBeInTheDocument();
    });

    it('clears recurrence day when switching patterns', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" recurrenceDay={1} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'daily');

      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(null);
    });
  });

  describe('Monthly Recurrence', () => {
    it('selects monthly recurrence', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'monthly');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith('monthly');
    });

    it('shows day of month selector for monthly recurrence', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="monthly" />);

      expect(screen.getByLabelText(/Day_Of_Month/i)).toBeInTheDocument();
    });

    it('displays all days 1-31', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="monthly" />);

      expect(screen.getByText('DAY 1')).toBeInTheDocument();
      expect(screen.getByText('DAY 15')).toBeInTheDocument();
      expect(screen.getByText('DAY 31')).toBeInTheDocument();
    });

    it('selects a specific day of month', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="monthly" />);

      const daySelect = screen.getByLabelText(/Day_Of_Month/i);
      await user.selectOptions(daySelect, '15');

      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(15);
    });

    it('shows info text when day is selected', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="monthly" recurrenceDay={15} />);

      expect(screen.getByText(/RECURS ON DAY 15 OF EACH MONTH/i)).toBeInTheDocument();
    });

    it('shows waiting message when no day selected', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="monthly" />);

      expect(screen.getByText(/WAITING FOR DATE SELECTION/i)).toBeInTheDocument();
    });
  });

  describe('Recurrence Switching', () => {
    it('changes from none to daily', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'daily');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith('daily');
      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(null);
    });

    it('changes from daily back to none', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="daily" />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'none');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith(null);
    });

    it('changes from weekly to monthly', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" recurrenceDay={1} />);

      const recurrenceSelect = screen.getByLabelText(/Recurrence_Pattern/i);
      await user.selectOptions(recurrenceSelect, 'monthly');

      expect(mockOnRecurrenceChange).toHaveBeenCalledWith('monthly');
      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(null);
    });
  });

  describe('Info Display', () => {
    it('does not show info when recurrence is none', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence={null} />);

      expect(screen.queryByText(/SCHEDULER:/i)).not.toBeInTheDocument();
    });

    it('shows info when recurrence is set', () => {
      render(<RecurrenceSelector {...defaultProps} recurrence="daily" />);

      expect(screen.getByText(/SCHEDULER:/i)).toBeInTheDocument();
    });

    it('correctly displays info for all weekdays', () => {
      const weekdays = [
        { day: 1, name: 'MONDAY' },
        { day: 2, name: 'TUESDAY' },
        { day: 3, name: 'WEDNESDAY' },
        { day: 4, name: 'THURSDAY' },
        { day: 5, name: 'FRIDAY' },
        { day: 6, name: 'SATURDAY' },
        { day: 7, name: 'SUNDAY' },
      ];

      weekdays.forEach(({ day, name }) => {
        const { rerender, unmount } = render(
          <RecurrenceSelector {...defaultProps} recurrence="weekly" recurrenceDay={day} />
        );

        expect(screen.getByText(new RegExp(`RECURS EVERY ${name}`, 'i'))).toBeInTheDocument();
        unmount();
      });
    });

    it('handles empty recurrence day value', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      const weekdaySelect = screen.getByLabelText(/Select_Weekday/i);
      fireEvent.change(weekdaySelect, { target: { value: '' } });

      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(null);
    });

    it('handles NaN recurrence day value', async () => {
      const user = userEvent.setup();
      render(<RecurrenceSelector {...defaultProps} recurrence="weekly" />);

      const weekdaySelect = screen.getByLabelText(/Select_Weekday/i);
      fireEvent.change(weekdaySelect, { target: { value: 'invalid' } });

      expect(mockOnRecurrenceDayChange).toHaveBeenCalledWith(null);
    });
  });
});
