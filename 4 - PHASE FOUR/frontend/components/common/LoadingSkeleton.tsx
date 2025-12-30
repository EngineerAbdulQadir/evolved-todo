/**
 * Loading skeletons for the Evolved OS interface.
 * Themes: Pure Black, Wireframe, Sharp Geometry.
 */

export function TaskListSkeleton() {
  return (
    <div className="space-y-0 border-t border-neutral-800">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="relative bg-black border-b border-neutral-800 p-4 animate-pulse group"
        >
          {/* Priority Indicator Strip (Left Border) */}
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-neutral-900"></div>

          <div className="flex items-start gap-4 pl-2">
            {/* Checkbox skeleton */}
            <div className="w-4 h-4 bg-neutral-900 border border-neutral-800 rounded-none mt-1 shrink-0"></div>

            <div className="flex-1 space-y-3 min-w-0">
              {/* Title & Actions Row */}
              <div className="flex justify-between items-start">
                <div className="h-4 bg-neutral-800 w-1/3 rounded-none"></div>
                {/* Action Buttons */}
                <div className="flex gap-2">
                  <div className="w-4 h-4 bg-neutral-900 rounded-none"></div>
                  <div className="w-4 h-4 bg-neutral-900 rounded-none"></div>
                </div>
              </div>

              {/* Description skeleton */}
              <div className="space-y-2">
                <div className="h-3 bg-neutral-900 w-2/3 rounded-none"></div>
              </div>

              {/* Metadata/Tags skeleton */}
              <div className="flex flex-wrap gap-2 pt-2">
                <div className="h-5 w-16 bg-neutral-900 border border-neutral-800 rounded-none"></div>
                <div className="h-5 w-20 bg-neutral-900 border border-neutral-800 rounded-none"></div>
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
    <div className="bg-black border border-white/10 rounded-none p-0">
      <div className="h-10 border-b border-white/10 bg-[#050505] mb-0"></div>
      <TaskListSkeleton />
    </div>
  );
}

/**
 * Loading skeleton for form components.
 */
export function FormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse p-2">
      {/* Title field */}
      <div className="space-y-2">
        <div className="flex justify-between">
          <div className="h-3 w-24 bg-neutral-800 rounded-none"></div>
        </div>
        <div className="h-10 bg-[#050505] border border-neutral-800 rounded-none w-full"></div>
      </div>

      {/* Description field */}
      <div className="space-y-2">
        <div className="h-3 w-32 bg-neutral-800 rounded-none"></div>
        <div className="h-24 bg-[#050505] border border-neutral-800 rounded-none w-full"></div>
      </div>

      {/* Priority & Date Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="h-3 w-20 bg-neutral-800 rounded-none"></div>
          <div className="h-10 bg-[#050505] border border-neutral-800 rounded-none w-full"></div>
        </div>
        <div className="space-y-2">
          <div className="h-3 w-24 bg-neutral-800 rounded-none"></div>
          <div className="h-10 bg-[#050505] border border-neutral-800 rounded-none w-full"></div>
        </div>
      </div>

      {/* Tags field */}
      <div className="space-y-2 border-t border-neutral-800 pt-4 mt-4">
        <div className="h-3 w-20 bg-neutral-800 rounded-none"></div>
        <div className="h-10 bg-[#050505] border border-neutral-800 rounded-none w-full"></div>
      </div>

      {/* Action buttons */}
      <div className="flex justify-end gap-0 pt-6 border-t border-neutral-800">
        <div className="h-10 w-24 bg-neutral-900 border border-neutral-800 rounded-none"></div>
        <div className="h-10 w-32 bg-neutral-800 rounded-none border-l border-neutral-900"></div>
      </div>
    </div>
  );
}

/**
 * Loading button component.
 */
export function ButtonLoading({ children, className, ...props }: any) {
  return (
    <button
      disabled
      className={`inline-flex items-center gap-2 opacity-70 cursor-not-allowed font-mono uppercase tracking-wider rounded-none ${className}`}
      {...props}
    >
      <svg
        className="animate-spin h-3 w-3 text-current"
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