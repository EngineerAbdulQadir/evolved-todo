"use client";

import { type ChangeEvent } from "react";
import { Repeat, Calendar, Hash, ChevronDown, RotateCw } from "lucide-react";

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

  // Sharp Industrial Styles
  const selectWrapperClass = "relative group";
  const selectClass = "w-full appearance-none bg-[#050505] border border-neutral-800 rounded-none px-4 py-3 text-xs font-mono uppercase text-white focus:outline-none focus:border-white transition-colors placeholder-neutral-600";
  const labelClass = "block text-[10px] font-mono font-bold uppercase tracking-widest text-neutral-500 mb-2 flex items-center gap-2";
  const chevronClass = "absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 pointer-events-none group-focus-within:text-white transition-colors";

  return (
    <div className="space-y-4 border-t border-white/10 pt-6 mt-4">
      
      {/* Header Label */}
      <div className="flex items-center gap-2 mb-2">
         <RotateCw className="w-3 h-3 text-white" />
         <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-white">Automation</span>
      </div>

      {/* Recurrence Pattern */}
      <div>
        <label htmlFor="recurrence" className={labelClass}>
          Cycle_Type
        </label>
        <div className={selectWrapperClass}>
          <select
            id="recurrence"
            value={recurrence || "none"}
            onChange={handleRecurrenceChange}
            className={selectClass}
          >
            <option value="none" className="bg-black text-neutral-500">Manual (Single Execution)</option>
            <option value="daily" className="bg-black text-white">Daily Loop (24h)</option>
            <option value="weekly" className="bg-black text-white">Weekly Loop (7d)</option>
            <option value="monthly" className="bg-black text-white">Monthly Loop (30d)</option>
          </select>
          <ChevronDown className={chevronClass} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Weekly: Weekday Selector */}
        {recurrence === "weekly" && (
            <div>
            <label htmlFor="recurrence_day" className={labelClass}>
                <Calendar className="w-3 h-3 text-neutral-600" /> Target_Weekday
            </label>
            <div className={selectWrapperClass}>
                <select
                id="recurrence_day"
                value={recurrenceDay || ""}
                onChange={handleRecurrenceDayChange}
                className={selectClass}
                >
                <option value="" className="bg-black text-neutral-600">-- SELECT DAY --</option>
                {WEEKDAYS.map((day) => (
                    <option key={day.value} value={day.value} className="bg-black text-white">
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
            <div>
            <label htmlFor="recurrence_day" className={labelClass}>
                <Hash className="w-3 h-3 text-neutral-600" /> Target_Ordinal
            </label>
            <div className={selectWrapperClass}>
                <select
                id="recurrence_day"
                value={recurrenceDay || ""}
                onChange={handleRecurrenceDayChange}
                className={selectClass}
                >
                <option value="" className="bg-black text-neutral-600">-- SELECT DATE (1-31) --</option>
                {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                    <option key={day} value={day} className="bg-black text-white">
                    DAY {day}
                    </option>
                ))}
                </select>
                <ChevronDown className={chevronClass} />
            </div>
            </div>
        )}
      </div>

      {/* System Output Message */}
      {recurrence && recurrence !== "none" && (
        <div className="mt-4 p-3 bg-neutral-900/10 border border-neutral-800 border-l-2 border-l-white flex flex-col gap-1">
          <span className="text-[9px] font-bold text-neutral-500 uppercase tracking-widest">Scheduler Output</span>
          <p className="text-[10px] font-mono text-neutral-300 uppercase leading-relaxed">
            {recurrence === "daily" && ">> Task regenerates T+24H post-completion."}
            
            {recurrence === "weekly" && recurrenceDay && 
              `>> Next instance: Every ${WEEKDAYS.find((d) => d.value === recurrenceDay)?.label}`
            }
            {recurrence === "weekly" && !recurrenceDay && ">> Awaiting day parameter..."}
            
            {recurrence === "monthly" && recurrenceDay && 
              `>> Next instance: Day ${recurrenceDay} of current month`
            }
            {recurrence === "monthly" && !recurrenceDay && ">> Awaiting date parameter..."}
          </p>
        </div>
      )}
    </div>
  );
}