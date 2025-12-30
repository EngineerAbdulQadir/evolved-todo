"use client";

import { Task } from "@/types/task";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (task: Task) => void;
  onAssignTask?: (taskId: number) => void; // Optional prop for task assignment
}

export function TaskList({ tasks, onToggleComplete, onDelete, onEdit, onAssignTask }: TaskListProps) {
  return (
    // "border-t" creates the top line of the grid.
    // "TaskItem" provides the bottom border for each row.
    <ul className="w-full flex flex-col border-t border-white/10">
      {tasks
        .filter(task => task !== undefined && task !== null) // Filter out undefined/null tasks
        .map((task) => (
          <li
            key={task.id}
            className="block w-full"
          >
            <TaskItem
              task={task}
              onToggleComplete={onToggleComplete}
              onDelete={onDelete}
              onEdit={onEdit}
              onAssignTask={onAssignTask}
            />
          </li>
        ))}
    </ul>
  );
}