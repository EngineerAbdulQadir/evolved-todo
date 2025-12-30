"use client";

import { useMemo } from "react";
import { AlertTriangle, Clock, Calendar, AlertCircle } from "lucide-react";

interface DueDateIndicatorProps {
  dueDate: string | null;
  dueTime?: string | null;
  isComplete: boolean;
}

/**
 * Component to display due date with visual indicators.
 * Theme: Pure Black, Sharp Edges, Industrial signals.
 */
export function DueDateIndicator({
  dueDate,
  dueTime,
  isComplete,
}: DueDateIndicatorProps) {
  const dueDateInfo = useMemo(() => {
    if (!dueDate) return null;
    if (isComplete) return null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const due = new Date(dueDate);
    due.setHours(0, 0, 0, 0);

    const diffTime = due.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      // Overdue: Red High Contrast
      const daysOverdue = Math.abs(diffDays);
      return {
        type: "overdue",
        label: `CRITICAL: -${daysOverdue}D`,
        tooltip: `Action Overdue by ${daysOverdue} days`,
        className: "text-red-500 bg-red-950/10 border-red-600",
        icon: AlertTriangle,
      };
    } else if (diffDays === 0) {
      // Due today: Amber Warning
      return {
        type: "today",
        label: dueTime ? `EXECUTE: ${dueTime}` : "EXECUTE: TODAY",
        tooltip: "Due Today",
        className: "text-amber-500 bg-amber-950/10 border-amber-500",
        icon: AlertCircle,
      };
    } else if (diffDays === 1) {
      // Due tomorrow: White High Priority
      return {
        type: "soon",
        label: dueTime ? `TMRW @ ${dueTime}` : "TOMORROW",
        tooltip: "Due Tomorrow",
        className: "text-white bg-black border-white",
        icon: Clock,
      };
    } else if (diffDays <= 7) {
      // Due within a week: Light Gray
      return {
        type: "soon",
        label: dueTime
          ? `T-${diffDays}D @ ${dueTime}`
          : `T-${diffDays} DAYS`,
        tooltip: `Due in ${diffDays} days`,
        className: "text-neutral-400 bg-black border-neutral-700",
        icon: Clock,
      };
    } else {
      // Future: Dark Gray (Passive)
      return {
        type: "future",
        label: dueTime
          ? `${due.toLocaleDateString()} ${dueTime}`
          : due.toLocaleDateString(),
        tooltip: `Due on ${due.toLocaleDateString()}`,
        className: "text-neutral-600 bg-black border-neutral-800",
        icon: Calendar,
      };
    }
  }, [dueDate, dueTime, isComplete]);

  if (!dueDateInfo) return null;

  const Icon = dueDateInfo.icon;

  return (
    <span
      title={dueDateInfo.tooltip}
      className={`inline-flex items-center gap-2 px-2 py-1 rounded-none text-[9px] font-mono font-bold uppercase tracking-widest border ${dueDateInfo.className}`}
    >
      <Icon className="w-3 h-3" strokeWidth={2} />
      {dueDateInfo.label}
    </span>
  );
}