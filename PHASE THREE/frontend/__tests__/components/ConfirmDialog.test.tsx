/**
 * Tests for ConfirmDialog component
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';

describe('ConfirmDialog Component', () => {
  const mockOnConfirm = jest.fn();
  const mockOnCancel = jest.fn();

  const defaultProps = {
    isOpen: true,
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
    onConfirm: mockOnConfirm,
    onCancel: mockOnCancel,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders when isOpen is true', () => {
      render(<ConfirmDialog {...defaultProps} />);

      expect(screen.getByText('Confirm Action')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to proceed?')).toBeInTheDocument();
    });

    it('does not render when isOpen is false', () => {
      render(<ConfirmDialog {...defaultProps} isOpen={false} />);

      expect(screen.queryByText('Confirm Action')).not.toBeInTheDocument();
    });

    it('renders default button texts', () => {
      render(<ConfirmDialog {...defaultProps} />);

      expect(screen.getByText('CONFIRM')).toBeInTheDocument();
      expect(screen.getByText('CANCEL')).toBeInTheDocument();
    });

    it('renders custom button texts', () => {
      render(
        <ConfirmDialog
          {...defaultProps}
          confirmText="DELETE"
          cancelText="GO BACK"
        />
      );

      expect(screen.getByText('DELETE')).toBeInTheDocument();
      expect(screen.getByText('GO BACK')).toBeInTheDocument();
      expect(screen.queryByText('CONFIRM')).not.toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onConfirm when confirm button is clicked', async () => {
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} />);

      const confirmButton = screen.getByText('CONFIRM');
      await user.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
      expect(mockOnCancel).not.toHaveBeenCalled();
    });

    it('calls onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(<ConfirmDialog {...defaultProps} />);

      const cancelButton = screen.getByText('CANCEL');
      await user.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
      expect(mockOnConfirm).not.toHaveBeenCalled();
    });

    it('calls onCancel when backdrop is clicked', async () => {
      const user = userEvent.setup();
      const { container } = render(<ConfirmDialog {...defaultProps} />);

      const backdrop = container.querySelector('.backdrop-blur-sm');
      if (backdrop) {
        await user.click(backdrop);
        expect(mockOnCancel).toHaveBeenCalledTimes(1);
      }
    });
  });

  describe('Variants', () => {
    it('renders with danger variant styling', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} variant="danger" />);

      const confirmButton = screen.getByText('CONFIRM');
      expect(confirmButton).toHaveClass('bg-red-600');

      const dialogPanel = container.querySelector('.border-red-600');
      expect(dialogPanel).toBeInTheDocument();
    });

    it('renders with warning variant styling', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} variant="warning" />);

      const confirmButton = screen.getByText('CONFIRM');
      expect(confirmButton).toHaveClass('bg-amber-500');

      const dialogPanel = container.querySelector('.border-amber-600');
      expect(dialogPanel).toBeInTheDocument();
    });

    it('renders with info variant styling', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} variant="info" />);

      const confirmButton = screen.getByText('CONFIRM');
      expect(confirmButton).toHaveClass('bg-white');

      const dialogPanel = container.querySelector('.border-white');
      expect(dialogPanel).toBeInTheDocument();
    });

    it('defaults to warning variant when no variant specified', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} />);

      const confirmButton = screen.getByText('CONFIRM');
      expect(confirmButton).toHaveClass('bg-amber-500');
    });
  });

  describe('Content Display', () => {
    it('displays custom title and message', () => {
      render(
        <ConfirmDialog
          {...defaultProps}
          title="Delete Task"
          message="This action cannot be undone. Are you sure?"
        />
      );

      expect(screen.getByText('Delete Task')).toBeInTheDocument();
      expect(screen.getByText('This action cannot be undone. Are you sure?')).toBeInTheDocument();
    });

    it('displays long messages correctly', () => {
      const longMessage = 'This is a very long message that should still be displayed correctly in the dialog. It contains multiple sentences to test text wrapping and formatting.';

      render(
        <ConfirmDialog
          {...defaultProps}
          message={longMessage}
        />
      );

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper button types to prevent form submission', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const confirmButton = screen.getByText('CONFIRM');
      const cancelButton = screen.getByText('CANCEL');

      expect(confirmButton).toHaveAttribute('type', 'button');
      expect(cancelButton).toHaveAttribute('type', 'button');
    });

    it('renders icons for each variant', () => {
      const variants: Array<'danger' | 'warning' | 'info'> = ['danger', 'warning', 'info'];

      variants.forEach((variant) => {
        const { container, unmount } = render(<ConfirmDialog {...defaultProps} variant={variant} />);

        // Check that an icon SVG is rendered
        const icon = container.querySelector('svg');
        expect(icon).toBeInTheDocument();

        unmount();
      });
    });
  });

  describe('Z-Index and Overlay', () => {
    it('renders with high z-index for modal overlay', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} />);

      const overlay = container.querySelector('.z-\\[100\\]');
      expect(overlay).toBeInTheDocument();
    });

    it('renders backdrop with blur effect', () => {
      const { container } = render(<ConfirmDialog {...defaultProps} />);

      const backdrop = container.querySelector('.backdrop-blur-sm');
      expect(backdrop).toBeInTheDocument();
    });
  });

  describe('Multiple Instances', () => {
    it('can render multiple dialogs with different props', () => {
      const { rerender } = render(<ConfirmDialog {...defaultProps} title="First Dialog" />);

      expect(screen.getByText('First Dialog')).toBeInTheDocument();

      rerender(<ConfirmDialog {...defaultProps} title="Second Dialog" />);

      expect(screen.getByText('Second Dialog')).toBeInTheDocument();
      expect(screen.queryByText('First Dialog')).not.toBeInTheDocument();
    });
  });

  describe('Button States', () => {
    it('confirm button has proper styling classes', () => {
      render(<ConfirmDialog {...defaultProps} variant="danger" />);

      const confirmButton = screen.getByText('CONFIRM');
      expect(confirmButton).toHaveClass('font-mono', 'font-bold', 'uppercase', 'tracking-widest');
    });

    it('cancel button has proper styling classes', () => {
      render(<ConfirmDialog {...defaultProps} />);

      const cancelButton = screen.getByText('CANCEL');
      expect(cancelButton).toHaveClass('font-mono', 'font-bold', 'uppercase', 'tracking-widest');
      expect(cancelButton).toHaveClass('bg-transparent');
    });
  });
});
