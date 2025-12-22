"use client";

import { ChangeEvent } from "react";
import { Calendar, Clock, X, AlertCircle } from "lucide-react";

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

  // Consistent Styles
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-cyan-500 mb-2 flex items-center gap-2";
  const inputClass = `
    block w-full pl-10 pr-3 py-2.5 bg-slate-950 border border-slate-700 rounded-sm text-white 
    placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 
    transition-all text-sm font-sans shadow-inner
    [color-scheme:dark]
    [&::-webkit-calendar-picker-indicator]:cursor-pointer
    [&::-webkit-calendar-picker-indicator]:opacity-50
    [&::-webkit-calendar-picker-indicator]:hover:opacity-100
    [&::-webkit-calendar-picker-indicator]:hover:bg-cyan-500/20
    [&::-webkit-calendar-picker-indicator]:rounded-sm
    [&::-webkit-calendar-picker-indicator]:p-1
    [&::-webkit-calendar-picker-indicator]:transition-all
  `;

  return (
    <div className="space-y-5">
      
      {/* Date Selection */}
      <div>
        <div className="flex justify-between items-end mb-2">
          <label htmlFor="due_date" className={labelClass}>
            <Calendar className="w-3 h-3" /> Execution_Date
          </label>
          
          {dueDate && (
            <button
              type="button"
              onClick={handleClear}
              className="text-[10px] font-mono uppercase tracking-wider text-red-400 hover:text-red-300 flex items-center gap-1 hover:underline decoration-red-500/30 underline-offset-4 transition-all"
            >
              <X className="w-3 h-3" /> Clear_Date
            </button>
          )}
        </div>

        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Calendar className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
          </div>
          <input
            type="date"
            id="due_date"
            value={dueDate || ""}
            onChange={handleDateChange}
            className={inputClass}
            placeholder="SELECT DATE"
          />
        </div>
      </div>

      {/* Time Selection (Conditional) */}
      {dueDate && (
        <div className="animate-in fade-in slide-in-from-top-2 duration-300">
          <label htmlFor="due_time" className={labelClass}>
            <Clock className="w-3 h-3" /> Execution_Time
          </label>
          
          <div className="relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Clock className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
            </div>
            <input
              type="time"
              id="due_time"
              value={dueTime || ""}
              onChange={handleTimeChange}
              className={inputClass}
            />
          </div>
          <p className="mt-1.5 text-[10px] text-slate-500 font-mono uppercase">
            * Optional precision timing
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 text-red-400 bg-red-950/20 p-2 rounded-sm border border-red-900/50 mt-2">
          <AlertCircle className="w-4 h-4" />
          <p className="text-xs font-mono">{error}</p>
        </div>
      )}
    </div>
  );
}