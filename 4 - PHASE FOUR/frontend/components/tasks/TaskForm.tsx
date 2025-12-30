"use client";

import { useState, useEffect } from "react";
import { Plus, X, Tag, FileText, AlertCircle, Hash, Check, ChevronDown } from "lucide-react";
import { DateTimePicker } from "../common/DateTimePicker";
import { RecurrenceSelector } from "./RecurrenceSelector";

type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";

interface TaskFormProps {
  mode?: "create" | "edit";
  initialTask?: {
    title: string;
    description: string;
    due_date?: string;
    due_time?: string;
    priority?: "low" | "medium" | "high";
    tags: string[];
    recurrence?: RecurrencePattern;
    recurrence_day?: number;
  };
  onSubmit: (taskData: any) => void;
  onCancel: () => void;
}

export function TaskForm({ mode = "create", initialTask, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title || "");
  const [description, setDescription] = useState(initialTask?.description || "");
  const [dueDate, setDueDate] = useState(initialTask?.due_date || "");
  const [dueTime, setDueTime] = useState(initialTask?.due_time || "");
  const [priority, setPriority] = useState<"low" | "medium" | "high">(
    initialTask?.priority || "medium"
  );
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>(initialTask?.tags || []);
  const [recurrence, setRecurrence] = useState<RecurrencePattern | null>(
    initialTask?.recurrence || null
  );
  const [recurrenceDay, setRecurrenceDay] = useState<number | null>(
    initialTask?.recurrence_day || null
  );

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title);
      setDescription(initialTask.description);
      setDueDate(initialTask.due_date || "");
      setDueTime(initialTask.due_time || "");
      setPriority(initialTask.priority || "medium");
      setTags(initialTask.tags);
      setRecurrence(initialTask.recurrence || null);
      setRecurrenceDay(initialTask.recurrence_day || null);
    }
  }, [initialTask]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title,
      description,
      due_date: dueDate || undefined,
      due_time: dueTime || undefined,
      priority,
      tags,
      recurrence: recurrence || undefined,
      recurrence_day: recurrenceDay || undefined,
    });

    if (mode === "create") {
      setTitle("");
      setDescription("");
      setDueDate("");
      setDueTime("");
      setPriority("medium");
      setTags([]);
      setRecurrence(null);
      setRecurrenceDay(null);
    }
  };

  const addTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      if (tagInput.trim() && !tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
        setTagInput("");
      }
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  // Sharp / Industrial Styles
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-neutral-500 mb-2 flex items-center gap-2";
  const inputClass = "block w-full px-4 py-3 bg-[#050505] border border-neutral-800 rounded-none text-white placeholder-neutral-700 focus:outline-none focus:border-white focus:bg-black transition-colors text-sm font-mono tracking-wide";
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      
      {/* Title */}
      <div>
        <label htmlFor="title" className={labelClass}>
          <FileText className="w-3 h-3 text-white" /> Objective_Title
        </label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="ENTER DIRECTIVE..."
          required
          autoFocus
          className={inputClass}
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className={labelClass}>
          <Hash className="w-3 h-3 text-white" /> Operational_Brief
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="ADD CONTEXT..."
          rows={3}
          className={inputClass}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Priority Selector */}
          <div>
            <label htmlFor="priority" className={labelClass}>
              <AlertCircle className="w-3 h-3 text-white" /> Priority_Class
            </label>
            <div className="relative group">
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as "low" | "medium" | "high")}
                className="w-full appearance-none px-4 py-3 bg-[#050505] border border-neutral-800 rounded-none text-white text-xs font-mono uppercase focus:outline-none focus:border-white transition-colors"
              >
                <option value="low">CLASS 3 (LOW)</option>
                <option value="medium">CLASS 2 (MEDIUM)</option>
                <option value="high">CLASS 1 (HIGH)</option>
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-600">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
          </div>

          {/* Date & Time Picker */}
          <div>
            <DateTimePicker
              dueDate={dueDate}
              dueTime={dueTime}
              onDueDateChange={(date) => setDueDate(date || '')}
              onDueTimeChange={(time) => setDueTime(time || '')}
            />
          </div>
      </div>

      {/* Recurrence Selector */}
      <RecurrenceSelector
        recurrence={recurrence}
        recurrenceDay={recurrenceDay}
        onRecurrenceChange={setRecurrence}
        onRecurrenceDayChange={setRecurrenceDay}
      />

      {/* Tags Input */}
      <div className="border-t border-white/10 pt-6 mt-2">
        <label htmlFor="tags" className={labelClass}>
          <Tag className="w-3 h-3 text-white" /> Metadata_Tags
        </label>
        
        {/* Active Tags Display */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {tags.map((tag, index) => (
              <span key={index} className="inline-flex items-center gap-1 pl-3 pr-2 py-1 text-[9px] font-mono uppercase tracking-widest bg-white text-black border border-white font-bold">
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="p-0.5 hover:bg-neutral-200 transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        
        <div className="flex gap-0">
          <input
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={addTag}
            placeholder="ADD TAG + ENTER"
            className={`${inputClass} border-r-0`}
          />
          <button
            type="button"
            onClick={() => {
              if (tagInput.trim() && !tags.includes(tagInput.trim())) {
                setTags([...tags, tagInput.trim()]);
                setTagInput("");
              }
            }}
            className="px-4 bg-neutral-900 border border-neutral-800 border-l-0 hover:bg-white hover:text-black hover:border-white transition-all rounded-none"
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-0 pt-8 border-t border-white/10 mt-6">
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-3 text-xs font-bold font-mono uppercase tracking-widest text-neutral-500 hover:text-white bg-transparent border border-neutral-800 hover:border-white transition-all rounded-none border-r-0"
        >
          Abort
        </button>
        <button
          type="submit"
          className="px-8 py-3 bg-white text-black text-xs font-bold font-mono uppercase tracking-widest rounded-none hover:bg-neutral-300 transition-all flex items-center gap-2 border border-white"
        >
          {mode === "edit" ? "Update_Protocol" : "Initialize_Sequence"}
          <Check className="w-4 h-4" />
        </button>
      </div>
    </form>
  );
}