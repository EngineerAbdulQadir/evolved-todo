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
  Hash 
} from "lucide-react";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => void;
  onDelete: (taskId: number) => void;
  onEdit: (task: Task) => void;
}

export function TaskItem({ task, onToggleComplete, onDelete, onEdit }: TaskItemProps) {
  
  // Priority Styles Configuration
  const priorityConfig = {
    high: {
      border: "bg-red-500",
      badge: "text-red-400 border-red-900/50 bg-red-950/30",
      icon: "text-red-500"
    },
    medium: {
      border: "bg-amber-500",
      badge: "text-amber-400 border-amber-900/50 bg-amber-950/30",
      icon: "text-amber-500"
    },
    low: {
      border: "bg-emerald-500",
      badge: "text-emerald-400 border-emerald-900/50 bg-emerald-950/30",
      icon: "text-emerald-500"
    },
  };

  const styles = task.priority 
    ? priorityConfig[task.priority] 
    : { border: "bg-slate-700", badge: "text-slate-400 bg-slate-900", icon: "text-slate-500" };

  return (
    <div className="group relative bg-slate-950/50 border border-slate-800 rounded-sm hover:border-cyan-500/30 hover:bg-slate-900/80 transition-all duration-300 overflow-hidden">
      
      {/* Priority Strip (Left Edge) */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${styles.border} shadow-[0_0_10px_rgba(0,0,0,0.5)]`} />

      <div className="flex items-start gap-4 p-4 pl-6">
        
        {/* Digital Checkbox */}
        <button
          onClick={() => onToggleComplete(task.id)}
          className="flex-shrink-0 mt-1 group/check relative"
          aria-label={task.is_complete ? "Mark incomplete" : "Mark complete"}
        >
          <div
            className={`w-5 h-5 rounded-sm border transition-all duration-300 flex items-center justify-center ${
              task.is_complete
                ? "bg-cyan-500 border-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]"
                : "bg-slate-900 border-slate-600 group-hover/check:border-cyan-400"
            }`}
          >
            {task.is_complete && <Check className="w-3.5 h-3.5 text-black stroke-[3]" />}
          </div>
        </button>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <h3
              className={`text-sm font-medium transition-colors duration-300 ${
                task.is_complete
                  ? "line-through text-slate-600 decoration-slate-700"
                  : "text-slate-100 group-hover:text-white"
              }`}
            >
              {task.title}
            </h3>
            
            {/* Action Buttons (Always visible on mobile, hover on desktop) */}
            <div className="flex items-center gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-200 -mt-1 -mr-2">
              <button
                onClick={() => onEdit(task)}
                className="p-1.5 text-slate-500 hover:text-cyan-400 hover:bg-cyan-950/30 rounded-sm transition-colors"
                title="Edit Protocol"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete(task.id)}
                className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-950/30 rounded-sm transition-colors"
                title="Purge Entry"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {task.description && (
            <p className={`mt-1.5 text-xs line-clamp-2 ${task.is_complete ? "text-slate-700" : "text-slate-400"}`}>
              {task.description}
            </p>
          )}

          {/* Metadata Grid */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            
            {/* Priority Badge */}
            {task.priority && (
              <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm text-[10px] font-mono font-bold uppercase border ${styles.badge}`}>
                <AlertCircle className="w-3 h-3" />
                {task.priority}
              </span>
            )}

            {/* Recurrence Indicator */}
            {task.recurrence && task.recurrence !== "none" && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm text-[10px] font-mono font-bold uppercase text-purple-400 bg-purple-950/30 border border-purple-900/50">
                <Repeat className="w-3 h-3" />
                {task.recurrence}
              </span>
            )}

            {/* Tags */}
            {task.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase text-slate-400 bg-slate-900 border border-slate-700"
              >
                <Hash className="w-2.5 h-2.5 text-slate-600" />
                {tag}
              </span>
            ))}

            {/* Spacer if we have indicators coming next */}
            {(task.due_date) && <div className="w-px h-3 bg-slate-800 mx-1"></div>}

            {/* Due Date */}
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