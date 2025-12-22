"use client";

import { useState, useRef, useEffect } from "react";
import { Priority } from "@/types/task";
import { 
  ListFilter, 
  Check, 
  X, 
  Activity, 
  AlertCircle, 
  Tag, 
  ChevronDown 
} from "lucide-react";

interface TaskFiltersProps {
  statusFilter: "all" | "active" | "completed";
  priorityFilter: Priority | "all";
  selectedTags: string[];
  availableTags: string[];
  onStatusChange: (status: "all" | "active" | "completed") => void;
  onPriorityChange: (priority: Priority | "all") => void;
  onTagToggle: (tag: string) => void;
  onClearFilters: () => void;
}

export function TaskFilters({
  statusFilter,
  priorityFilter,
  selectedTags,
  availableTags,
  onStatusChange,
  onPriorityChange,
  onTagToggle,
  onClearFilters,
}: TaskFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const hasActiveFilters =
    statusFilter !== "all" ||
    priorityFilter !== "all" ||
    selectedTags.length > 0;

  // Calculate active filter count for badge
  const activeCount = (statusFilter !== "all" ? 1 : 0) + 
                      (priorityFilter !== "all" ? 1 : 0) + 
                      selectedTags.length;

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

  // Priority Styles Map
  const priorityStyles = {
    high: "text-red-400 border-red-900/50 hover:bg-red-950/50 hover:border-red-500",
    medium: "text-amber-400 border-amber-900/50 hover:bg-amber-950/50 hover:border-amber-500",
    low: "text-emerald-400 border-emerald-900/50 hover:bg-emerald-950/50 hover:border-emerald-500",
    all: "text-slate-400 border-slate-700 hover:bg-slate-800 hover:text-white"
  };

  const activePriorityStyle = {
    high: "bg-red-950/50 border-red-500 text-red-400 shadow-[0_0_10px_rgba(248,113,113,0.2)]",
    medium: "bg-amber-950/50 border-amber-500 text-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.2)]",
    low: "bg-emerald-950/50 border-emerald-500 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.2)]",
    all: "bg-cyan-950/30 border-cyan-500 text-cyan-400"
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 px-4 py-2.5 text-xs font-mono font-bold uppercase tracking-wide
          bg-slate-950 border rounded-sm transition-all duration-200
          ${isOpen || hasActiveFilters
            ? "border-cyan-500 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.1)]" 
            : "border-slate-700 text-slate-300 hover:border-cyan-500/50 hover:text-white"
          }
        `}
      >
        <ListFilter className="w-3 h-3" />
        <span>FILTERS</span>
        {activeCount > 0 && (
          <span className="flex items-center justify-center w-4 h-4 text-[9px] bg-cyan-500 text-slate-950 rounded-full font-bold">
            {activeCount}
          </span>
        )}
        <ChevronDown
          className={`w-3 h-3 text-slate-500 transition-transform duration-200 ${isOpen ? "rotate-180 text-cyan-400" : ""}`}
        />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute left-0 md:left-auto md:right-0 z-50 mt-2 w-72 md:w-80 bg-slate-900 border border-slate-700 rounded-sm shadow-2xl animate-in fade-in zoom-in-95 duration-100 backdrop-blur-xl">
          <div className="p-4 space-y-6">
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-widest">
                Configure View
              </span>
              {hasActiveFilters && (
                <button
                  onClick={onClearFilters}
                  className="text-[10px] font-mono text-red-400 hover:text-red-300 flex items-center gap-1 uppercase tracking-wider"
                >
                  <X className="w-3 h-3" /> Reset
                </button>
              )}
            </div>

            {/* Status Section */}
            <div>
              <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-cyan-500 uppercase tracking-widest mb-3">
                <Activity className="w-3 h-3" /> Status_Mode
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(["all", "active", "completed"] as const).map((status) => (
                  <button
                    key={status}
                    onClick={() => onStatusChange(status)}
                    className={`
                      px-2 py-1.5 text-xs font-mono font-bold uppercase tracking-wide rounded-sm border transition-all
                      ${statusFilter === status 
                        ? "bg-cyan-950/50 border-cyan-500 text-cyan-400 shadow-sm" 
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-600 hover:text-white"
                      }
                    `}
                  >
                    {status}
                  </button>
                ))}
              </div>
            </div>

            {/* Priority Section */}
            <div>
              <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-cyan-500 uppercase tracking-widest mb-3">
                <AlertCircle className="w-3 h-3" /> Priority_Level
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => onPriorityChange("all")}
                  className={`px-2 py-1.5 text-xs font-mono font-bold uppercase tracking-wide rounded-sm border transition-all ${
                    priorityFilter === "all" ? activePriorityStyle.all : priorityStyles.all
                  }`}
                >
                  ALL LEVELS
                </button>
                {(["high", "medium", "low"] as const).map((p) => (
                  <button
                    key={p}
                    onClick={() => onPriorityChange(p)}
                    className={`px-2 py-1.5 text-xs font-mono font-bold uppercase tracking-wide rounded-sm border transition-all ${
                      priorityFilter === p ? activePriorityStyle[p] : priorityStyles[p]
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Tags Section */}
            {availableTags.length > 0 && (
              <div>
                <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-cyan-500 uppercase tracking-widest mb-3">
                  <Tag className="w-3 h-3" /> Filter_Tags
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto custom-scrollbar">
                  {availableTags.map((tag) => {
                    const isActive = selectedTags.includes(tag);
                    return (
                      <button
                        key={tag}
                        onClick={() => onTagToggle(tag)}
                        className={`
                          flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase tracking-wide rounded-sm border transition-all
                          ${isActive
                            ? "bg-purple-950/50 border-purple-500 text-purple-300"
                            : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-600 hover:text-white"
                          }
                        `}
                      >
                        {tag}
                        {isActive && <Check className="w-2 h-2" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}