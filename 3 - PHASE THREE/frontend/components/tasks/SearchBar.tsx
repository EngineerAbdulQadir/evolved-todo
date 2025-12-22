"use client";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchBar({ 
  value, 
  onChange, 
  placeholder = "SEARCH_DATABASE...",
  className 
}: SearchBarProps) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={`
        block w-full py-3 px-4 bg-black border border-neutral-800 rounded-none
        text-white placeholder-neutral-700 font-mono text-xs uppercase tracking-widest
        focus:outline-none focus:border-white focus:bg-[#050505] focus:ring-0
        transition-colors
        ${className || ""}
      `}
    />
  );
}