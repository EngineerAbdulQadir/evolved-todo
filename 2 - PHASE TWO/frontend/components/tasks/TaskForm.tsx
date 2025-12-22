"use client";

import { useState, useEffect } from "react";
import { Plus, X, Tag, FileText, AlertCircle, Hash, Check } from "lucide-react";
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
    priority: "low" | "medium" | "high";
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
      setPriority(initialTask.priority);
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

  // Shared Styles
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-cyan-500 mb-2 flex items-center gap-2";
  const inputClass = "block w-full px-3 py-2.5 bg-slate-950 border border-slate-700 rounded-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all text-sm font-sans shadow-inner";
  
  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      
      {/* Title */}
      <div>
        <label htmlFor="title" className={labelClass}>
          <FileText className="w-3 h-3" /> Task_Objective
        </label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="ENTER PRIMARY OBJECTIVE..."
          required
          autoFocus
          className={inputClass}
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className={labelClass}>
          <Hash className="w-3 h-3" /> Detailed_Brief
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="ADD OPERATIONAL DETAILS..."
          rows={3}
          className={inputClass}
        />
      </div>

      {/* Priority Selector */}
      <div>
        <label htmlFor="priority" className={labelClass}>
          <AlertCircle className="w-3 h-3" /> Priority_Level
        </label>
        <div className="relative group">
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as "low" | "medium" | "high")}
            className="w-full appearance-none px-3 py-2.5 bg-slate-950 border border-slate-700 rounded-sm text-white text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono uppercase"
          >
            <option value="low">LOW PRIORITY</option>
            <option value="medium">MEDIUM PRIORITY</option>
            <option value="high">HIGH PRIORITY</option>
          </select>
          {/* Custom Arrow */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </div>
        </div>
      </div>

      {/* Date & Time Picker */}
      <div className="border-t border-slate-800 pt-5 mt-2">
        <DateTimePicker
          dueDate={dueDate}
          dueTime={dueTime}
          onDueDateChange={setDueDate}
          onDueTimeChange={setDueTime}
        />
      </div>

      {/* Recurrence Selector */}
      <RecurrenceSelector
        recurrence={recurrence}
        recurrenceDay={recurrenceDay}
        onRecurrenceChange={setRecurrence}
        onRecurrenceDayChange={setRecurrenceDay}
      />

      {/* Tags Input */}
      <div className="border-t border-slate-800 pt-5 mt-2">
        <label htmlFor="tags" className={labelClass}>
          <Tag className="w-3 h-3" /> Metadata_Tags
        </label>
        
        {/* Active Tags Display */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {tags.map((tag, index) => (
              <span key={index} className="inline-flex items-center gap-1 pl-2 pr-1 py-1 text-[10px] font-mono uppercase tracking-wide rounded-sm bg-cyan-950/30 border border-cyan-500/30 text-cyan-300">
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="p-0.5 hover:bg-cyan-900/50 rounded-sm text-cyan-500 hover:text-white transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        
        <div className="flex gap-2">
          <input
            id="tags"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={addTag}
            placeholder="ADD TAG (PRESS ENTER)"
            className={`${inputClass} flex-1`}
          />
          <button
            type="button"
            onClick={() => {
              if (tagInput.trim() && !tags.includes(tagInput.trim())) {
                setTags([...tags, tagInput.trim()]);
                setTagInput("");
              }
            }}
            className="px-3 bg-cyan-500 hover:bg-cyan-400 text-slate-900 rounded-sm flex items-center justify-center transition-colors"
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-6 border-t border-slate-800 mt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-xs font-bold font-mono uppercase tracking-widest text-slate-400 hover:text-white border border-transparent hover:border-slate-600 rounded-sm transition-all"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-6 py-2 bg-cyan-500 text-slate-950 text-xs font-bold font-mono uppercase tracking-widest rounded-sm hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] flex items-center gap-2"
        >
          {mode === "edit" ? "Update_Protocol" : "Initialize_Task"}
          <Check className="w-4 h-4" />
        </button>
      </div>
    </form>
  );
}