"use client";

import { useState, useRef, useEffect } from "react";
import { ArrowUpDown, ChevronDown, Check } from "lucide-react";

export type SortField = "created_at" | "due_date" | "priority" | "title" | "completed";
export type SortOrder = "asc" | "desc";

export interface SortOption {
  field: SortField;
  order: SortOrder;
  label: string;
}

interface SortDropdownProps {
  value: SortOption;
  onChange: (option: SortOption) => void;
}

const SORT_OPTIONS: SortOption[] = [
  { field: "created_at", order: "desc", label: "Newest First" },
  { field: "created_at", order: "asc", label: "Oldest First" },
  { field: "due_date", order: "asc", label: "Due Date (Soonest)" },
  { field: "due_date", order: "desc", label: "Due Date (Latest)" },
  { field: "priority", order: "desc", label: "Priority (High > Low)" },
  { field: "priority", order: "asc", label: "Priority (Low > High)" },
  { field: "title", order: "asc", label: "Title (A-Z)" },
  { field: "title", order: "desc", label: "Title (Z-A)" },
  { field: "completed", order: "asc", label: "Pending First" },
  { field: "completed", order: "desc", label: "Completed First" },
];

export function SortDropdown({ value, onChange }: SortDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  const currentLabel = SORT_OPTIONS.find(
    (opt) => opt.field === value.field && opt.order === value.order
  )?.label || "Newest First";

  const handleSelect = (option: SortOption) => {
    onChange(option);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 px-4 py-2.5 text-xs font-mono font-bold uppercase tracking-wide
          bg-slate-950 border rounded-sm transition-all duration-200
          ${isOpen 
            ? "border-cyan-500 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.2)]" 
            : "border-slate-700 text-slate-300 hover:border-cyan-500/50 hover:text-white"
          }
        `}
      >
        <ArrowUpDown className="w-3 h-3 text-cyan-500" />
        <span className="truncate max-w-[150px]">Sort: {currentLabel}</span>
        <ChevronDown
          className={`w-3 h-3 text-slate-500 transition-transform duration-200 ${isOpen ? "rotate-180 text-cyan-400" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 z-50 mt-2 w-64 bg-slate-900 border border-slate-700 rounded-sm shadow-2xl animate-in fade-in zoom-in-95 duration-100">
          <div className="py-1">
            <div className="px-3 py-2 text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800">
              Sort Configuration
            </div>
            <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
              {SORT_OPTIONS.map((option, index) => {
                const isSelected = option.field === value.field && option.order === value.order;
                return (
                  <button
                    key={index}
                    onClick={() => handleSelect(option)}
                    className={`
                      w-full text-left px-4 py-2.5 text-xs font-mono uppercase tracking-wide flex items-center justify-between group transition-colors
                      ${isSelected
                        ? "bg-cyan-950/30 text-cyan-400 border-l-2 border-cyan-500"
                        : "text-slate-400 hover:bg-slate-800 hover:text-white border-l-2 border-transparent"
                      }
                    `}
                  >
                    <span>{option.label}</span>
                    {isSelected && <Check className="w-3 h-3 text-cyan-500" />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}