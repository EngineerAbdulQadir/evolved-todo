"use client";

import { type ChangeEvent } from "react";
import { Repeat, Calendar, Hash, ChevronDown } from "lucide-react";

type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";

interface RecurrenceSelectorProps {
  recurrence: RecurrencePattern | null;
  recurrenceDay: number | null;
  onRecurrenceChange: (recurrence: RecurrencePattern | null) => void;
  onRecurrenceDayChange: (day: number | null) => void;
}

const WEEKDAYS = [
  { value: 1, label: "Monday" },
  { value: 2, label: "Tuesday" },
  { value: 3, label: "Wednesday" },
  { value: 4, label: "Thursday" },
  { value: 5, label: "Friday" },
  { value: 6, label: "Saturday" },
  { value: 7, label: "Sunday" },
];

export function RecurrenceSelector({
  recurrence,
  recurrenceDay,
  onRecurrenceChange,
  onRecurrenceDayChange,
}: RecurrenceSelectorProps) {
  const handleRecurrenceChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as RecurrencePattern;
    onRecurrenceChange(value === "none" ? null : value);

    // Clear recurrence_day when switching patterns
    onRecurrenceDayChange(null);
  };

  const handleRecurrenceDayChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const value = parseInt(e.target.value, 10);
    onRecurrenceDayChange(isNaN(value) ? null : value);
  };

  // Shared classes for consistent input styling
  const selectWrapperClass = "relative group";
  const selectClass = "w-full appearance-none bg-slate-950 border border-slate-700 text-white rounded-sm px-3 py-2.5 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono shadow-inner";
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-cyan-500 mb-2 flex items-center gap-2";
  const chevronClass = "absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none group-focus-within:text-cyan-400 transition-colors";

  return (
    <div className="space-y-5 border-t border-slate-800 pt-5 mt-2">
      {/* Recurrence Pattern */}
      <div>
        <label htmlFor="recurrence" className={labelClass}>
          <Repeat className="w-3 h-3" /> Recurrence_Pattern
        </label>
        <div className={selectWrapperClass}>
          <select
            id="recurrence"
            value={recurrence || "none"}
            onChange={handleRecurrenceChange}
            className={selectClass}
          >
            <option value="none" className="bg-slate-950 text-slate-400">NO REPEAT (ONE-TIME)</option>
            <option value="daily" className="bg-slate-950 text-white">DAILY CYCLE</option>
            <option value="weekly" className="bg-slate-950 text-white">WEEKLY CYCLE</option>
            <option value="monthly" className="bg-slate-950 text-white">MONTHLY CYCLE</option>
          </select>
          <ChevronDown className={chevronClass} />
        </div>
      </div>

      {/* Weekly: Weekday Selector */}
      {recurrence === "weekly" && (
        <div className="animate-in fade-in slide-in-from-top-2 duration-300">
          <label htmlFor="recurrence_day" className={labelClass}>
            <Calendar className="w-3 h-3" /> Select_Weekday
          </label>
          <div className={selectWrapperClass}>
            <select
              id="recurrence_day"
              value={recurrenceDay || ""}
              onChange={handleRecurrenceDayChange}
              className={selectClass}
            >
              <option value="" className="bg-slate-950 text-slate-500">-- SELECT DAY --</option>
              {WEEKDAYS.map((day) => (
                <option key={day.value} value={day.value} className="bg-slate-950 text-white">
                  {day.label.toUpperCase()}
                </option>
              ))}
            </select>
            <ChevronDown className={chevronClass} />
          </div>
        </div>
      )}

      {/* Monthly: Day of Month Selector */}
      {recurrence === "monthly" && (
        <div className="animate-in fade-in slide-in-from-top-2 duration-300">
          <label htmlFor="recurrence_day" className={labelClass}>
            <Hash className="w-3 h-3" /> Day_Of_Month
          </label>
          <div className={selectWrapperClass}>
            <select
              id="recurrence_day"
              value={recurrenceDay || ""}
              onChange={handleRecurrenceDayChange}
              className={selectClass}
            >
              <option value="" className="bg-slate-950 text-slate-500">-- SELECT DATE (1-31) --</option>
              {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                <option key={day} value={day} className="bg-slate-950 text-white">
                  DAY {day}
                </option>
              ))}
            </select>
            <ChevronDown className={chevronClass} />
          </div>
        </div>
      )}

      {/* System Status / Info text */}
      {recurrence && recurrence !== "none" && (
        <div className="flex items-start gap-2 px-3 py-2 bg-slate-900 border border-slate-800 rounded-sm">
          <div className="w-1 h-full bg-cyan-500 rounded-full min-h-[12px] mt-1"></div>
          <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wide leading-relaxed">
            <span className="text-cyan-600 font-bold mr-1">SCHEDULER:</span>
            {recurrence === "daily" && "TASK WILL REGENERATE T+24H UPON COMPLETION"}
            
            {recurrence === "weekly" && recurrenceDay && 
              `RECURS EVERY ${WEEKDAYS.find((d) => d.value === recurrenceDay)?.label.toUpperCase()}`
            }
            {recurrence === "weekly" && !recurrenceDay && "WAITING FOR DAY SELECTION..."}
            
            {recurrence === "monthly" && recurrenceDay && 
              `RECURS ON DAY ${recurrenceDay} OF EACH MONTH`
            }
            {recurrence === "monthly" && !recurrenceDay && "WAITING FOR DATE SELECTION..."}
          </p>
        </div>
      )}
    </div>
  );
}