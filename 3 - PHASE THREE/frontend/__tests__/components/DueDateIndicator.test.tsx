/**
 * Tests for DueDateIndicator component (T204).
 */

import { render, screen } from "@testing-library/react";
import { DueDateIndicator } from "@/components/tasks/DueDateIndicator";

describe("DueDateIndicator", () => {
  it("shows overdue indicator for past due dates", () => {
    // Create a date 3 days ago
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 3);
    const dueDateStr = pastDate.toISOString().split("T")[0];

    render(
      <DueDateIndicator dueDate={dueDateStr} dueTime={null} isComplete={false} />
    );

    expect(screen.getByText(/CRITICAL: -3d/i)).toBeInTheDocument();
  });

  it("shows 'Due today' for tasks due today", () => {
    const today = new Date().toISOString().split("T")[0];

    render(
      <DueDateIndicator dueDate={today} dueTime={null} isComplete={false} />
    );

    expect(screen.getByText(/EXECUTE: TODAY/i)).toBeInTheDocument();
  });

  it("shows 'Due in X days' for future tasks", () => {
    const future = new Date();
    future.setDate(future.getDate() + 5);
    const dueDateStr = future.toISOString().split("T")[0];

    render(
      <DueDateIndicator dueDate={dueDateStr} dueTime={null} isComplete={false} />
    );

    expect(screen.getByText(/T-5 DAYS/i)).toBeInTheDocument();
  });

  it("shows due time when provided", () => {
    const today = new Date().toISOString().split("T")[0];

    render(
      <DueDateIndicator
        dueDate={today}
        dueTime="14:30"
        isComplete={false}
      />
    );

    expect(screen.getByText(/EXECUTE: 14:30/i)).toBeInTheDocument();
  });

  it("shows nothing for completed tasks", () => {
    const today = new Date().toISOString().split("T")[0];

    const { container } = render(
      <DueDateIndicator dueDate={today} dueTime={null} isComplete={true} />
    );

    expect(container.firstChild).toBeNull();
  });

  it("shows nothing when no due date", () => {
    const { container } = render(
      <DueDateIndicator dueDate={null} dueTime={null} isComplete={false} />
    );

    expect(container.firstChild).toBeNull();
  });
});
