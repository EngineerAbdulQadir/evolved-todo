"use client";

import { ChangeEvent } from "react";
import { Calendar, Clock, X, AlertTriangle } from "lucide-react";

interface DateTimePickerProps {
  dueDate: string | null;
  dueTime: string | null;
  onDueDateChange: (date: string | null) => void;
  onDueTimeChange: (time: string | null) => void;
  error?: string;
}

export function DateTimePicker({
  dueDate,
  dueTime,
  onDueDateChange,
  onDueTimeChange,
  error,
}: DateTimePickerProps) {
  
  const handleDateChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onDueDateChange(value || null);
    // Clear time if date is cleared
    if (!value) onDueTimeChange(null);
  };

  const handleTimeChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onDueTimeChange(value || null);
  };

  const handleClear = () => {
    onDueDateChange(null);
    onDueTimeChange(null);
  };

  // Sharp, Industrial Styles
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-neutral-500 mb-2 flex items-center gap-2";
  
  const inputClass = `
    block w-full pl-10 pr-3 py-3 bg-[#050505] border border-neutral-800 rounded-none text-white 
    placeholder-neutral-700 focus:outline-none focus:border-white focus:bg-black 
    transition-all text-xs font-mono uppercase tracking-wider
    [color-scheme:dark]
    [&::-webkit-calendar-picker-indicator]:opacity-70
    [&::-webkit-calendar-picker-indicator]:hover:opacity-100
    [&::-webkit-calendar-picker-indicator]:cursor-pointer
  `;

  return (
    <div className="space-y-4 border-l border-white/10 pl-4 ml-1">
      
      {/* Date Selection */}
      <div className="relative">
        <div className="flex justify-between items-end mb-2">
          <label htmlFor="due_date" className={labelClass}>
            <Calendar className="w-3 h-3 text-white" /> Target_Date
          </label>
          
          {dueDate && (
            <button
              type="button"
              onClick={handleClear}
              className="text-[9px] font-mono uppercase tracking-wider text-neutral-500 hover:text-white flex items-center gap-1 transition-colors border border-transparent hover:border-neutral-800 px-1"
            >
              <X className="w-3 h-3" /> Clear
            </button>
          )}
        </div>

        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Calendar className="h-4 w-4 text-white group-focus-within:text-neutral-300 transition-colors" />
          </div>
          <input
            type="date"
            id="due_date"
            value={dueDate || ""}
            onChange={handleDateChange}
            className={inputClass}
            placeholder="YYYY-MM-DD"
          />
        </div>
      </div>

      {/* Time Selection (Conditional Slide-In) */}
      {dueDate && (
        <div>
          <label htmlFor="due_time" className={labelClass}>
            <Clock className="w-3 h-3 text-white" /> T-Minus / Time
          </label>
          
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Clock className="h-4 w-4 text-white group-focus-within:text-neutral-300 transition-colors" />
            </div>
            <input
              type="time"
              id="due_time"
              value={dueTime || ""}
              onChange={handleTimeChange}
              className={inputClass}
            />
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 text-red-500 bg-red-950/10 p-2 border border-red-900/30">
          <AlertTriangle className="w-3 h-3" />
          <p className="text-[10px] font-mono uppercase">{error}</p>
        </div>
      )}
    </div>
  );
}