"use client";

import { AlertTriangle, Info, AlertCircle, ShieldAlert } from "lucide-react";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "info";
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = "CONFIRM",
  cancelText = "CANCEL",
  variant = "warning",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  // Theme configuration for the sharp aesthetic
  const variantStyles = {
    danger: {
      icon: AlertTriangle,
      iconColor: "text-red-500",
      borderColor: "border-red-600",
      bgColor: "bg-red-950/5",
      button: "bg-red-600 text-white hover:bg-red-500 border-red-600",
      titleColor: "text-red-500"
    },
    warning: {
      icon: AlertCircle,
      iconColor: "text-amber-500",
      borderColor: "border-amber-600",
      bgColor: "bg-amber-950/5",
      button: "bg-amber-500 text-black hover:bg-amber-400 border-amber-500",
      titleColor: "text-amber-500"
    },
    info: {
      icon: Info,
      iconColor: "text-white",
      borderColor: "border-white",
      bgColor: "bg-neutral-900/50",
      button: "bg-white text-black hover:bg-neutral-200 border-white",
      titleColor: "text-white"
    },
  };

  const styles = variantStyles[variant];
  const Icon = styles.icon;

  return (
    <div className="fixed inset-0 z-[100] overflow-y-auto">
      {/* Backdrop: Solid black with blur to focus attention */}
      <div
        className="fixed inset-0 bg-black/90 backdrop-blur-sm transition-opacity"
        onClick={onCancel}
      />

      {/* Centering Wrapper */}
      <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        
        {/* Dialog Panel: Sharp corners, solid black, distinct colored border */}
        <div 
          className={`
            relative transform overflow-hidden bg-black text-left shadow-[0_0_0_1px_rgba(255,255,255,0.1)] transition-all sm:my-8 sm:w-full sm:max-w-lg 
            border-l-4 ${styles.borderColor} rounded-none
          `}
        >
          {/* Header Area */}
          <div className={`p-8 ${styles.bgColor} border-b border-white/5`}>
            <div className="flex items-start gap-6">
              {/* Sharp Icon Box */}
              <div 
                className={`flex-shrink-0 flex items-center justify-center h-12 w-12 border ${styles.borderColor} bg-black`}
              >
                <Icon className={`h-6 w-6 ${styles.iconColor}`} strokeWidth={1.5} />
              </div>

              {/* Text Content */}
              <div className="flex-1 text-left">
                <h3 className={`text-lg font-mono font-bold uppercase tracking-widest leading-none mb-3 ${styles.titleColor}`}>
                  {title}
                </h3>
                <p className="text-xs font-mono text-neutral-400 leading-relaxed uppercase tracking-wide">
                  {message}
                </p>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="bg-[#050505] px-6 py-4 sm:flex sm:flex-row-reverse gap-3 border-t border-white/10">
            <button
              type="button"
              onClick={onConfirm}
              className={`
                inline-flex w-full justify-center px-6 py-3 text-xs font-mono font-bold uppercase tracking-widest transition-all sm:w-auto border rounded-none
                ${styles.button}
              `}
            >
              {confirmText}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="mt-2 inline-flex w-full justify-center px-6 py-3 text-xs font-mono font-bold uppercase tracking-widest text-neutral-500 bg-transparent border border-neutral-800 hover:border-white hover:text-white sm:mt-0 sm:w-auto transition-all rounded-none"
            >
              {cancelText}
            </button>
          </div>
          
          {/* Tech decoration corner */}
          <div className="absolute top-0 right-0 p-1">
             <div className={`w-2 h-2 ${styles.borderColor} border-t border-r`}></div>
          </div>
        </div>
      </div>
    </div>
  );
}