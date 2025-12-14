"use client";

import { useMemo } from "react";
import { AlertTriangle, Clock, Calendar, AlertCircle } from "lucide-react";

interface DueDateIndicatorProps {
  dueDate: string | null;
  dueTime?: string | null;
  isComplete: boolean;
}

/**
 * Component to display due date with visual indicators and relative time.
 * Updated for Evolved OS aesthetic (Dark mode, Technical look).
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
      // Overdue: Red Warning
      const daysOverdue = Math.abs(diffDays);
      return {
        type: "overdue",
        label: `CRITICAL: -${daysOverdue}d`,
        tooltip: `Overdue by ${daysOverdue} days`,
        className: "text-red-400 bg-red-950/30 border-red-500/50 shadow-[0_0_10px_rgba(248,113,113,0.1)]",
        icon: AlertTriangle,
      };
    } else if (diffDays === 0) {
      // Due today: Amber Alert
      return {
        type: "today",
        label: dueTime ? `DUE: ${dueTime}` : "DUE: TODAY",
        tooltip: "Due Today",
        className: "text-amber-400 bg-amber-950/30 border-amber-500/50 shadow-[0_0_10px_rgba(251,191,36,0.1)]",
        icon: AlertCircle,
      };
    } else if (diffDays === 1) {
      // Due tomorrow: Cyan Info
      return {
        type: "soon",
        label: dueTime ? `TMRW @ ${dueTime}` : "TOMORROW",
        tooltip: "Due Tomorrow",
        className: "text-cyan-400 bg-cyan-950/30 border-cyan-500/50",
        icon: Clock,
      };
    } else if (diffDays <= 7) {
      // Due within a week: Cyan/Slate Info
      return {
        type: "soon",
        label: dueTime
          ? `IN ${diffDays}d @ ${dueTime}`
          : `IN ${diffDays} DAYS`,
        tooltip: `Due in ${diffDays} days`,
        className: "text-cyan-300 bg-cyan-950/20 border-cyan-900/50",
        icon: Clock,
      };
    } else {
      // Future: Slate Passive
      return {
        type: "future",
        label: dueTime
          ? `${due.toLocaleDateString()} ${dueTime}`
          : due.toLocaleDateString(),
        tooltip: `Due on ${due.toLocaleDateString()}`,
        className: "text-slate-400 bg-slate-900/50 border-slate-700",
        icon: Calendar,
      };
    }
  }, [dueDate, dueTime, isComplete]);

  if (!dueDateInfo) return null;

  const Icon = dueDateInfo.icon;

  return (
    <span
      title={dueDateInfo.tooltip}
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-sm text-[10px] font-mono font-bold uppercase tracking-wider border backdrop-blur-sm ${dueDateInfo.className}`}
    >
      <Icon className="w-3 h-3" strokeWidth={2.5} />
      {dueDateInfo.label}
    </span>
  );
}