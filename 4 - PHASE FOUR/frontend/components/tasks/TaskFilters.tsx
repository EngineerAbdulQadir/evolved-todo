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
  ChevronDown,
  Filter
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

  // Sharp Monochrome Priority Styles
  const priorityStyles = {
    high: "text-neutral-500 hover:text-white border-b border-transparent hover:border-white",
    medium: "text-neutral-500 hover:text-white border-b border-transparent hover:border-white",
    low: "text-neutral-500 hover:text-white border-b border-transparent hover:border-white",
    all: "text-neutral-500 hover:text-white border-b border-transparent hover:border-white"
  };

  const activePriorityStyle = {
    high: "text-white bg-black border border-white font-bold",
    medium: "text-white bg-black border border-white font-bold",
    low: "text-white bg-black border border-white font-bold",
    all: "text-white bg-black border border-white font-bold"
  };

  return (
    <div className="relative h-full" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          h-full flex items-center justify-between gap-4 px-4 min-w-[140px]
          bg-black border rounded-none transition-all duration-200
          text-xs font-mono font-bold uppercase tracking-widest
          ${isOpen || hasActiveFilters
            ? "border-white text-white bg-[#050505]" 
            : "border-neutral-800 text-neutral-400 hover:border-white hover:text-white"
          }
        `}
      >
        <div className="flex items-center gap-2">
           <Filter className="w-3 h-3" />
           <span>Filters</span>
           {activeCount > 0 && (
             <span className="flex items-center justify-center w-4 h-4 text-[9px] bg-white text-black font-bold">
               {activeCount}
             </span>
           )}
        </div>
        <ChevronDown
          className={`w-3 h-3 text-neutral-600 transition-transform duration-200 ${isOpen ? "rotate-180 text-white" : ""}`}
        />
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute left-0 z-50 mt-0 w-80 bg-black border border-white border-t-0 shadow-2xl rounded-none">
          <div className="p-0">
            
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-800 bg-[#050505]">
              <span className="text-[9px] font-mono font-bold text-neutral-500 uppercase tracking-widest">
                System Filters
              </span>
              {hasActiveFilters && (
                <button
                  onClick={onClearFilters}
                  className="text-[9px] font-mono text-white hover:text-neutral-300 flex items-center gap-1 uppercase tracking-wider transition-colors border border-white px-2 py-0.5"
                >
                  <X className="w-3 h-3" /> Clear
                </button>
              )}
            </div>

            <div className="p-4 space-y-6">
               {/* Status Section */}
               <div>
                 <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-white uppercase tracking-widest mb-3">
                   <Activity className="w-3 h-3 text-neutral-500" /> Status
                 </label>
                 <div className="grid grid-cols-3 gap-0 border border-neutral-800">
                   {(["all", "active", "completed"] as const).map((status) => (
                     <button
                       key={status}
                       onClick={() => onStatusChange(status)}
                       className={`
                         py-2 text-[10px] font-mono uppercase tracking-wide transition-all border-r border-neutral-800 last:border-r-0
                         ${statusFilter === status 
                           ? "bg-white text-black font-bold" 
                           : "bg-black text-neutral-500 hover:text-white hover:bg-neutral-900"
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
                 <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-white uppercase tracking-widest mb-3">
                   <AlertCircle className="w-3 h-3 text-neutral-500" /> Priority
                 </label>
                 <div className="grid grid-cols-2 gap-2">
                   <button
                     onClick={() => onPriorityChange("all")}
                     className={`py-2 text-[10px] font-mono uppercase tracking-wide border transition-all ${
                       priorityFilter === "all" ? "bg-white text-black border-white font-bold" : "border-neutral-800 text-neutral-500 hover:border-white hover:text-white"
                     }`}
                   >
                     Any Priority
                   </button>
                   {(["high", "medium", "low"] as const).map((p) => (
                     <button
                       key={p}
                       onClick={() => onPriorityChange(p)}
                       className={`py-2 text-[10px] font-mono uppercase tracking-wide border transition-all ${
                         priorityFilter === p ? "bg-white text-black border-white font-bold" : "border-neutral-800 text-neutral-500 hover:border-white hover:text-white"
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
                   <label className="flex items-center gap-2 text-[10px] font-mono font-bold text-white uppercase tracking-widest mb-3">
                     <Tag className="w-3 h-3 text-neutral-500" /> Tags
                   </label>
                   <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto custom-scrollbar border-t border-neutral-800 pt-3">
                     {availableTags.map((tag) => {
                       const isActive = selectedTags.includes(tag);
                       return (
                         <button
                           key={tag}
                           onClick={() => onTagToggle(tag)}
                           className={`
                             flex items-center gap-1 px-2 py-1 text-[10px] font-mono uppercase tracking-wide border transition-all
                             ${isActive
                               ? "bg-white text-black border-white font-bold"
                               : "bg-black border-neutral-800 text-neutral-500 hover:border-white hover:text-white"
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
        </div>
      )}
    </div>
  );
}