"use client"

import * as React from "react"
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "lucide-react"
import {
  DayPicker,
  getDefaultClassNames,
  type DayButton,
} from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button, buttonVariants } from "@/components/ui/button"

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  captionLayout = "label",
  buttonVariant = "ghost",
  formatters,
  components,
  ...props
}: React.ComponentProps<typeof DayPicker> & {
  buttonVariant?: React.ComponentProps<typeof Button>["variant"]
}) {
  const defaultClassNames = getDefaultClassNames()

  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn(
        "bg-black border border-white/10 p-3 shadow-none rounded-none font-sans",
        // CSS Variable for cell size
        "[--cell-size:36px]", 
        String.raw`rtl:**:[.rdp-button\_next>svg]:rotate-180`,
        String.raw`rtl:**:[.rdp-button\_previous>svg]:rotate-180`,
        className
      )}
      captionLayout={captionLayout}
      formatters={{
        formatMonthDropdown: (date) =>
          date.toLocaleString("default", { month: "short" }),
        ...formatters,
      }}
      classNames={{
        root: cn("w-fit", defaultClassNames.root),
        months: cn(
          "flex gap-4 flex-col md:flex-row relative",
          defaultClassNames.months
        ),
        month: cn("flex flex-col w-full gap-4", defaultClassNames.month),
        nav: cn(
          "flex items-center gap-1 w-full absolute top-0 inset-x-0 justify-between",
          defaultClassNames.nav
        ),
        // Navigation Buttons (Sharp & High Contrast Hover)
        button_previous: cn(
          buttonVariants({ variant: "ghost" }),
          "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 hover:bg-neutral-900 hover:text-white hover:border hover:border-white/20 text-neutral-400 rounded-none transition-all",
          defaultClassNames.button_previous
        ),
        button_next: cn(
          buttonVariants({ variant: "ghost" }),
          "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 hover:bg-neutral-900 hover:text-white hover:border hover:border-white/20 text-neutral-400 rounded-none transition-all",
          defaultClassNames.button_next
        ),
        month_caption: cn(
          "flex items-center justify-center h-9 w-full",
          defaultClassNames.month_caption
        ),
        dropdowns: cn(
          "w-full flex items-center text-sm font-medium justify-center h-9 gap-1.5",
          defaultClassNames.dropdowns
        ),
        // Month Title (Monospace & Uppercase)
        caption_label: cn(
          "text-sm font-mono font-bold uppercase tracking-widest text-white",
          defaultClassNames.caption_label
        ),
        table: "w-full border-collapse space-y-1",
        weekdays: cn("flex", defaultClassNames.weekdays),
        // Weekday headers (Mo, Tu, We...)
        weekday: cn(
          "text-neutral-500 rounded-none w-9 font-mono text-[10px] uppercase tracking-wider font-normal select-none",
          defaultClassNames.weekday
        ),
        week: cn("flex w-full mt-2", defaultClassNames.week),
        day: cn(
          "relative w-9 h-9 p-0 text-center text-sm focus-within:relative focus-within:z-20",
          defaultClassNames.day
        ),
        range_start: "day-range-start",
        range_end: "day-range-end",
        // Outside days
        outside: cn(
          "text-neutral-800 opacity-50 aria-selected:bg-neutral-900/50 aria-selected:text-neutral-500",
          defaultClassNames.outside
        ),
        disabled: cn(
          "text-neutral-800 opacity-50",
          defaultClassNames.disabled
        ),
        hidden: cn("invisible", defaultClassNames.hidden),
        ...classNames,
      }}
      components={{
        Root: ({ className, rootRef, ...props }) => {
          return (
            <div
              data-slot="calendar"
              ref={rootRef}
              className={cn(className)}
              {...props}
            />
          )
        },
        Chevron: ({ className, orientation, ...props }) => {
          if (orientation === "left") {
            return (
              <ChevronLeftIcon className={cn("h-4 w-4", className)} {...props} />
            )
          }

          if (orientation === "right") {
            return (
              <ChevronRightIcon
                className={cn("h-4 w-4", className)}
                {...props}
              />
            )
          }

          return (
            <ChevronDownIcon className={cn("h-4 w-4", className)} {...props} />
          )
        },
        DayButton: CalendarDayButton,
        ...components,
      }}
      {...props}
    />
  )
}

function CalendarDayButton({
  className,
  day,
  modifiers,
  ...props
}: React.ComponentProps<typeof DayButton>) {
  const defaultClassNames = getDefaultClassNames()

  const ref = React.useRef<HTMLButtonElement>(null)
  React.useEffect(() => {
    if (modifiers.focused) ref.current?.focus()
  }, [modifiers.focused])

  return (
    <Button
      ref={ref}
      variant="ghost"
      size="icon"
      data-day={day.date.toLocaleDateString()}
      data-selected-single={
        modifiers.selected &&
        !modifiers.range_start &&
        !modifiers.range_end &&
        !modifiers.range_middle
      }
      data-today={modifiers.today}
      className={cn(
        // Base Button Styles (Sharp corners, mono font)
        "h-9 w-9 p-0 font-normal rounded-none transition-all duration-200 font-mono text-xs",
        
        // Default Text Color
        "text-neutral-400 hover:bg-neutral-900 hover:text-white hover:border hover:border-white/10",
        
        // Selected State (Solid White, Black Text)
        "data-[selected-single=true]:bg-white data-[selected-single=true]:text-black data-[selected-single=true]:font-bold data-[selected-single=true]:border-white data-[selected-single=true]:hover:bg-neutral-200",
        
        // Today State (Outlined White)
        "data-[today=true]:text-white data-[today=true]:border data-[today=true]:border-white data-[today=true]:bg-black",
        
        // Selected & Today Conflict override
        "data-[selected-single=true]:data-[today=true]:bg-white data-[selected-single=true]:data-[today=true]:text-black",

        defaultClassNames.day,
        className
      )}
      {...props}
    />
  )
}

export { Calendar, CalendarDayButton }