"use client";

import { AlertTriangle, Info, AlertCircle } from "lucide-react";

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

  const variantStyles = {
    danger: {
      icon: AlertTriangle,
      iconColor: "text-red-500",
      iconBg: "bg-red-950/30",
      borderColor: "border-red-900/50",
      glow: "shadow-[0_0_30px_rgba(220,38,38,0.2)]",
      button: "bg-red-600 hover:bg-red-500 text-white shadow-[0_0_15px_rgba(220,38,38,0.4)]",
    },
    warning: {
      icon: AlertCircle,
      iconColor: "text-amber-500",
      iconBg: "bg-amber-950/30",
      borderColor: "border-amber-900/50",
      glow: "shadow-[0_0_30px_rgba(245,158,11,0.2)]",
      button: "bg-amber-600 hover:bg-amber-500 text-white shadow-[0_0_15px_rgba(245,158,11,0.4)]",
    },
    info: {
      icon: Info,
      iconColor: "text-cyan-500",
      iconBg: "bg-cyan-950/30",
      borderColor: "border-cyan-900/50",
      glow: "shadow-[0_0_30px_rgba(6,182,212,0.2)]",
      button: "bg-cyan-600 hover:bg-cyan-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]",
    },
  };

  const styles = variantStyles[variant];
  const Icon = styles.icon;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop with Blur */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onCancel}
      />

      {/* Dialog Position */}
      <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        
        {/* Dialog Panel */}
        <div 
          className={`
            relative transform overflow-hidden rounded-sm bg-slate-950 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg border 
            ${styles.borderColor} ${styles.glow}
          `}
        >
          {/* Header Strip */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-slate-700 to-transparent opacity-50"></div>

          <div className="p-6">
            <div className="sm:flex sm:items-start">
              {/* Icon Circle */}
              <div 
                className={`mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full sm:mx-0 sm:h-10 sm:w-10 ${styles.iconBg}`}
              >
                <Icon className={`h-6 w-6 ${styles.iconColor}`} strokeWidth={2} />
              </div>

              {/* Text Content */}
              <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                <h3 className="text-base font-mono font-bold uppercase tracking-widest text-white leading-6">
                  {title}
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-slate-400 font-sans leading-relaxed">
                    {message}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="bg-slate-900/50 border-t border-slate-800 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6 gap-3">
            <button
              type="button"
              onClick={onConfirm}
              className={`
                inline-flex w-full justify-center rounded-sm px-4 py-2 text-xs font-mono font-bold uppercase tracking-widest shadow-sm ring-1 ring-inset ring-transparent transition-all sm:w-auto
                ${styles.button}
              `}
            >
              {confirmText}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="mt-3 inline-flex w-full justify-center rounded-sm bg-transparent px-4 py-2 text-xs font-mono font-bold uppercase tracking-widest text-slate-400 shadow-sm ring-1 ring-inset ring-slate-700 hover:bg-slate-800 hover:text-white sm:mt-0 sm:w-auto transition-all"
            >
              {cancelText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}