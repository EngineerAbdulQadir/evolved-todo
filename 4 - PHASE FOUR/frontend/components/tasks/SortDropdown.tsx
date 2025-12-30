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
    <div className="relative h-full" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          h-full flex items-center justify-between gap-4 px-4 min-w-[200px]
          bg-black border transition-all duration-200 rounded-none
          text-xs font-mono font-bold uppercase tracking-widest
          ${isOpen 
            ? "border-white text-white bg-[#050505]" 
            : "border-neutral-800 text-neutral-400 hover:border-white hover:text-white"
          }
        `}
      >
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-3 h-3" />
          <span className="truncate">{currentLabel}</span>
        </div>
        <ChevronDown
          className={`w-3 h-3 transition-transform duration-200 ${isOpen ? "rotate-180 text-white" : "text-neutral-600"}`}
        />
      </button>

      {isOpen && (
        <div className="absolute right-0 z-50 mt-0 w-64 bg-black border border-white border-t-0 shadow-xl rounded-none">
          <div className="py-0">
            <div className="px-4 py-2 text-[9px] font-mono font-bold text-neutral-500 uppercase tracking-widest border-b border-neutral-800 bg-[#050505]">
              Ordering Protocol
            </div>
            <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
              {SORT_OPTIONS.map((option, index) => {
                const isSelected = option.field === value.field && option.order === value.order;
                return (
                  <button
                    key={index}
                    onClick={() => handleSelect(option)}
                    className={`
                      w-full text-left px-4 py-3 text-[10px] font-mono uppercase tracking-wider flex items-center justify-between group transition-colors border-b border-neutral-900 last:border-0
                      ${isSelected
                        ? "bg-white text-black font-bold"
                        : "text-neutral-400 hover:bg-neutral-900 hover:text-white"
                      }
                    `}
                  >
                    <span>{option.label}</span>
                    {isSelected && <Check className="w-3 h-3 text-black" />}
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