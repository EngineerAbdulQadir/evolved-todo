/**
 * Loading skeletons for the Evolved OS interface.
 * Themes: Dark, Technical, Sharp Geometry.
 */

export function TaskListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="relative bg-slate-950/50 border border-slate-800 rounded-sm p-4 animate-pulse overflow-hidden"
        >
          {/* Priority Strip Skeleton */}
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-slate-800"></div>

          <div className="flex items-start gap-4 pl-2">
            {/* Checkbox skeleton */}
            <div className="w-5 h-5 bg-slate-800 rounded-sm mt-0.5 shrink-0"></div>

            <div className="flex-1 space-y-3 min-w-0">
              {/* Title & Actions Row */}
              <div className="flex justify-between items-start">
                <div className="h-4 bg-slate-800 rounded-sm w-1/3"></div>
                <div className="flex gap-2">
                  <div className="w-6 h-6 bg-slate-900 rounded-sm"></div>
                  <div className="w-6 h-6 bg-slate-900 rounded-sm"></div>
                </div>
              </div>

              {/* Description skeleton */}
              <div className="space-y-1.5">
                <div className="h-3 bg-slate-900/50 rounded-sm w-3/4"></div>
                <div className="h-3 bg-slate-900/50 rounded-sm w-1/2"></div>
              </div>

              {/* Metadata/Tags skeleton */}
              <div className="flex flex-wrap gap-2 pt-1">
                <div className="h-5 w-16 bg-slate-800 rounded-sm"></div>
                <div className="h-5 w-20 bg-slate-800 rounded-sm"></div>
                <div className="h-5 w-24 bg-slate-800/50 rounded-sm border border-slate-800"></div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="bg-slate-900/30 rounded-sm border border-slate-800 p-6 backdrop-blur-sm">
      <TaskListSkeleton />
    </div>
  );
}

/**
 * Loading skeleton for form components (T219).
 */
export function FormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Title field */}
      <div className="space-y-2">
        <div className="h-3 w-24 bg-slate-800 rounded-sm"></div>
        <div className="h-10 bg-slate-900 border border-slate-800 rounded-sm w-full"></div>
      </div>

      {/* Description field */}
      <div className="space-y-2">
        <div className="h-3 w-32 bg-slate-800 rounded-sm"></div>
        <div className="h-24 bg-slate-900 border border-slate-800 rounded-sm w-full"></div>
      </div>

      {/* Priority & Date Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="h-3 w-20 bg-slate-800 rounded-sm"></div>
          <div className="h-10 bg-slate-900 border border-slate-800 rounded-sm w-full"></div>
        </div>
        <div className="space-y-2">
          <div className="h-3 w-24 bg-slate-800 rounded-sm"></div>
          <div className="h-10 bg-slate-900 border border-slate-800 rounded-sm w-full"></div>
        </div>
      </div>

      {/* Tags field */}
      <div className="space-y-2 border-t border-slate-800 pt-4">
        <div className="h-3 w-20 bg-slate-800 rounded-sm"></div>
        <div className="h-10 bg-slate-900 border border-slate-800 rounded-sm w-full"></div>
      </div>

      {/* Action buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
        <div className="h-9 w-20 bg-slate-800 rounded-sm"></div>
        <div className="h-9 w-32 bg-slate-800 rounded-sm"></div>
      </div>
    </div>
  );
}

/**
 * Loading button component (T219).
 */
export function ButtonLoading({ children, className, ...props }: any) {
  return (
    <button
      disabled
      className={`inline-flex items-center gap-2 opacity-70 cursor-not-allowed font-mono uppercase tracking-wider ${className}`}
      {...props}
    >
      <svg
        className="animate-spin h-4 w-4 text-current"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      {children}
    </button>
  );
}