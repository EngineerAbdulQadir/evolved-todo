"use client";

import { Task } from "@/types/task";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (task: Task) => void;
}

export function TaskList({ tasks, onToggleComplete, onDelete, onEdit }: TaskListProps) {
  return (
    // "border-t" creates the top line of the grid. 
    // "TaskItem" provides the bottom border for each row.
    <ul className="w-full flex flex-col border-t border-white/10">
      {tasks.map((task) => (
        <li 
          key={task.id} 
          className="block w-full animate-in fade-in slide-in-from-bottom-1 duration-300"
        >
          <TaskItem
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            onEdit={onEdit}
          />
        </li>
      ))}
    </ul>
  );
}