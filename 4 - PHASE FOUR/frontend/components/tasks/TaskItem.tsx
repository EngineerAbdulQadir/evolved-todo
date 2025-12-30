"use client";

import type { Task } from "@/types/task";
import { DueDateIndicator } from "./DueDateIndicator";
import {
  Check,
  Edit2,
  Trash2,
  Repeat,
  Tag,
  AlertCircle,
  Hash,
  MoreVertical,
  Folder,
  User
} from "lucide-react";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onEdit: (task: Task) => void;
  onAssignTask?: (taskId: number) => void; // Optional prop for task assignment
}

export function TaskItem({ task, onToggleComplete, onDelete, onEdit, onAssignTask }: TaskItemProps) {
  // Defensive check: if task is undefined, don't render anything
  if (!task) {
    return null;
  }

  // Sharp Priority Colors
  const priorityConfig = {
    high: {
      border: "bg-red-600",
      text: "text-red-500",
      badge: "border-red-600 text-red-500 bg-black"
    },
    medium: {
      border: "bg-amber-500",
      text: "text-amber-500",
      badge: "border-amber-500 text-amber-500 bg-black"
    },
    low: {
      border: "bg-neutral-500",
      text: "text-neutral-500",
      badge: "border-neutral-500 text-neutral-500 bg-black"
    },
  };

  const styles = task.priority
    ? priorityConfig[task.priority]
    : { border: "bg-neutral-800", text: "text-neutral-500", badge: "border-neutral-800 text-neutral-500" };

  return (
    <div className={`
      group relative bg-black border-b border-white/10 transition-all duration-200 task-card
      hover:bg-[#050505]
      ${task.is_complete ? 'opacity-60 grayscale' : 'opacity-100'}
    `}>

      {/* Priority Strip (Left Edge) */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${styles.border}`} />

      <div className="flex items-start gap-5 p-5 pl-6">

        {/* Sharp Checkbox */}
        <button
          onClick={() => onToggleComplete(task.id)}
          className="flex-shrink-0 mt-1 group/check relative"
          aria-label={task.is_complete ? "Mark incomplete" : "Mark complete"}
        >
          <div
            className={`
              w-5 h-5 border rounded-none transition-all duration-200 flex items-center justify-center
              ${task.is_complete
                ? "bg-white border-white"
                : "bg-black border-neutral-600 hover:border-white"
              }
            `}
          >
            {task.is_complete && <Check className="w-3.5 h-3.5 text-black stroke-[3]" />}
          </div>
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start gap-4">

            {/* Title */}
            <h3
              className={`text-sm font-mono font-bold tracking-wide transition-colors duration-200 ${
                task.is_complete
                  ? "line-through text-neutral-600 decoration-neutral-600"
                  : "text-white group-hover:text-white"
              }`}
            >
              {task.title}
            </h3>

            {/* Action Buttons (Hidden until hover) */}
            <div className="flex items-center gap-0 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-200 -mt-1 -mr-2 border border-transparent lg:group-hover:border-white/20 lg:group-hover:bg-black">
              <button
                onClick={() => onEdit(task)}
                className="p-2 text-neutral-500 hover:text-white hover:bg-white/10 transition-colors"
                title="Edit Protocol"
              >
                <Edit2 className="w-3.5 h-3.5" />
              </button>
              <div className="w-px h-4 bg-white/10 hidden lg:block"></div>
              <button
                onClick={() => onDelete(task.id)}
                className="p-2 text-neutral-500 hover:text-red-500 hover:bg-red-950/20 transition-colors"
                title="Purge Entry"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Description */}
          {task.description && (
            <p className={`mt-2 text-xs font-mono leading-relaxed line-clamp-2 ${task.is_complete ? "text-neutral-700" : "text-neutral-500"}`}>
              {task.description}
            </p>
          )}

          {/* Metadata Grid */}
          <div className="mt-4 flex flex-wrap items-center gap-3">

            {/* Priority Badge */}
            {task.priority && (
              <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9px] font-mono font-bold uppercase border ${styles.badge}`}>
                <AlertCircle className="w-3 h-3" />
                {task.priority}
              </span>
            )}

            {/* Project Context */}
            {task.project_id && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9px] font-mono uppercase text-blue-400 border border-blue-400/30 bg-blue-950/20">
                <Folder className="w-2.5 h-2.5" />
                Project
              </span>
            )}

            {/* Assignee */}
            {task.assigned_to && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9px] font-mono uppercase text-green-400 border border-green-400/30 bg-green-950/20">
                <User className="w-2.5 h-2.5" />
                Assigned
              </span>
            )}

            {/* Recurrence Indicator */}
            {task.recurrence && task.recurrence !== "none" && (
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9px] font-mono font-bold uppercase text-white bg-black border border-white/40">
                <Repeat className="w-3 h-3" />
                {task.recurrence}
              </span>
            )}

            {/* Tags */}
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-none text-[9px] font-mono uppercase text-neutral-400 border border-neutral-800 bg-[#0A0A0A]"
              >
                <Hash className="w-2.5 h-2.5 text-neutral-600" />
                {tag}
              </span>
            ))}

            {/* Divider if needed */}
            {(task.due_date) && <div className="h-3 w-px bg-neutral-800 mx-1"></div>}

            {/* Due Date Indicator */}
            <DueDateIndicator
              dueDate={task.due_date}
              dueTime={task.due_time}
              isComplete={task.is_complete}
            />
          </div>
        </div>
      </div>
    </div>
  );
}