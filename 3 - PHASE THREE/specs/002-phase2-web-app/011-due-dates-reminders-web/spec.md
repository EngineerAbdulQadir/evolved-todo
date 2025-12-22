# Feature Specification: Due Dates and Time Reminders (Web)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Create due date and time management for web application allowing users to set deadlines, view upcoming tasks, and receive visual reminders for overdue items"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Due Date on Task (Priority: P2)

As a user, I want to set a due date when creating or editing a task, so I can track deadlines and time-sensitive work.

**Why this priority**: Important for deadline management, core feature for users who need time tracking.

**Independent Test**: Can be fully tested by creating a task "Submit report" with due date "2025-12-15", saving it, and verifying the task displays with "Due Dec 15, 2025".

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I select due date "2025-12-15" from date picker and save, **Then** the task displays with formatted due date "Due Dec 15, 2025"
2. **Given** I am editing a task, **When** I add a due date, **Then** the due date is saved and displayed
3. **Given** I am creating a task, **When** I don't set a due date, **Then** the task is created without due date (optional field)

---

### User Story 2 - Set Due Time (Specific Hour) (Priority: P3)

As a user, I want to set a specific time for my due date (not just the day), so I can track tasks that need to be done at particular times.

**Why this priority**: Advanced feature that's only useful for time-specific tasks, not needed for all tasks.

**Independent Test**: Can be fully tested by setting due date "2025-12-11" with time "09:00", saving, and verifying task displays "Due Dec 11, 2025 at 9:00 AM".

**Acceptance Scenarios**:

1. **Given** I set due date "2025-12-11" and time "09:00", **When** I save the task, **Then** it displays "Due Dec 11, 2025 at 9:00 AM"
2. **Given** I set a due date, **When** I don't set a time, **Then** only the date is shown (time is optional)
3. **Given** I am using time picker, **When** I select time, **Then** I can choose hours and minutes

---

### User Story 3 - View Overdue Tasks with Visual Indicator (Priority: P2)

As a user, I want overdue tasks (due date in the past, task incomplete) to be highlighted in red, so I can immediately see what's past deadline.

**Why this priority**: Critical for deadline awareness, helps users prioritize overdue work.

**Independent Test**: Can be fully tested by creating a task with due date "2025-12-01" (past date), viewing it today, and verifying it shows "Overdue" in red highlighting.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with due date in the past, **When** I view my task list, **Then** the task shows "Overdue" in red text with red indicator
2. **Given** I complete an overdue task, **When** I view it, **Then** the overdue indicator is removed (completed tasks don't show as overdue)
3. **Given** I have multiple overdue tasks, **When** I view my dashboard, **Then** I see an overdue task count prominently displayed

---

### User Story 4 - View Tasks Due Today with Visual Indicator (Priority: P2)

As a user, I want tasks due today to be highlighted in yellow/orange, so I can prioritize today's deadlines.

**Why this priority**: Important for daily focus, helps users manage today's workload.

**Independent Test**: Can be fully tested by creating a task with today's date as due date and verifying it shows "Due today" with yellow/orange highlighting.

**Acceptance Scenarios**:

1. **Given** I have a task due today, **When** I view my task list, **Then** it shows "Due today" with yellow/orange highlighting
2. **Given** I complete a task due today, **When** I view it, **Then** the "due today" indicator is removed

---

### User Story 5 - View Upcoming Tasks (Due Soon) (Priority: P2)

As a user, I want to see tasks due in the next 7 days with a visual indicator, so I can plan ahead.

**Why this priority**: Useful for planning but less urgent than overdue and due today indicators.

**Independent Test**: Can be fully tested by creating tasks due tomorrow and in 3 days, and verifying they show "Due tomorrow" or "Due in 3 days" indicators.

**Acceptance Scenarios**:

1. **Given** I have a task due tomorrow, **When** I view my task list, **Then** it shows "Due tomorrow" with clock icon
2. **Given** I have a task due in 3 days, **When** I view my task list, **Then** it shows "Due in 3 days"
3. **Given** I have a task due in 8 days, **When** I view my task list, **Then** it shows the formatted date "Due Dec 18, 2025" without special highlighting

---

### User Story 6 - Filter/Sort by Due Date (Priority: P2)

As a user, I want to sort my tasks by due date to see which deadlines are approaching first, so I can prioritize deadline-driven work.

**Why this priority**: Essential for deadline-based workflow, already covered in Sort Tasks spec but worth noting here.

**Independent Test**: Can be fully tested by selecting "Sort by: Due Date" and verifying tasks appear in order of earliest due date first.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Due Date", **When** I view my tasks, **Then** overdue tasks appear first, then tasks due today, then upcoming, then no due date
2. **Given** I filter by "Overdue", **When** I view results, **Then** only incomplete tasks with due dates in past are shown

---

### Edge Cases

- What happens when a task's due date is set to midnight (00:00)?
- What happens when a task due today becomes overdue at midnight (timezone considerations)?
- What happens when a user changes their device timezone and views tasks?
- What happens when a user sets a due time without a due date?
- What happens when a recurring task's due date passes before it's completed?
- What happens when filtering by "Due This Week" on Sunday (week boundary)?

## Requirements *(mandatory)*

### Functional Requirements

**Due Date Setting:**
- **FR-001**: System MUST allow users to set due date when creating or editing tasks
- **FR-002**: Due date MUST be a valid date (ISO 8601 format: YYYY-MM-DD)
- **FR-003**: System MUST provide date picker UI for selecting due dates
- **FR-004**: Due date MUST be optional (tasks can have no due date)
- **FR-005**: System MUST allow clearing/removing due date from tasks

**Due Time Setting:**
- **FR-006**: System MUST allow users to optionally set specific time for due date
- **FR-007**: Due time MUST be a valid time (HH:MM format, 24-hour internally)
- **FR-008**: Due time can only be set if due date is also set
- **FR-009**: System MUST display due time in 12-hour format with AM/PM

**Visual Indicators:**
- **FR-010**: Overdue tasks (due date in past, incomplete) MUST show "Overdue" in red with red indicator
- **FR-011**: Tasks due today MUST show "Due today" in yellow/orange with special icon
- **FR-012**: Tasks due tomorrow MUST show "Due tomorrow" with clock icon
- **FR-013**: Tasks due in 2-7 days MUST show "Due in X days"
- **FR-014**: Tasks due beyond 7 days MUST show formatted date "Due Dec 18, 2025"
- **FR-015**: Completed tasks MUST not show overdue indicators

**Dashboard Summary:**
- **FR-016**: Dashboard MUST show count of overdue tasks prominently
- **FR-017**: Dashboard MUST show count of tasks due today
- **FR-018**: Dashboard MUST show count of tasks due this week
- **FR-019**: Clicking these counts MUST filter task list accordingly

**Date/Time Display:**
- **FR-020**: System MUST display due dates in user-friendly format (e.g., "Dec 15, 2025")
- **FR-021**: System MUST display relative dates for recent tasks (today, tomorrow, yesterday)
- **FR-022**: System MUST show both date and time when time is set (e.g., "Due today at 2:00 PM")

**Filtering & Sorting:**
- **FR-023**: System MUST provide "Overdue" filter showing only incomplete tasks with past due dates
- **FR-024**: System MUST provide "Due Today" filter
- **FR-025**: System MUST provide "Due This Week" filter
- **FR-026**: System MUST provide "No Due Date" filter
- **FR-027**: Sort by due date MUST order: overdue → due today → upcoming → no due date

**API Integration:**
- **FR-028**: Backend MUST validate due date format before saving
- **FR-029**: Backend MUST allow null due_date and due_time (optional fields)
- **FR-030**: Backend MUST store due dates in UTC (convert from user timezone)
- **FR-031**: Backend MUST calculate overdue status based on current date/time

### Key Entities

- **Task**: Standard task entity with due date fields:
  - due_date (nullable date)
  - due_time (nullable time)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Due date selection takes less than 10 seconds using date picker
- **SC-002**: 100% of overdue tasks are correctly identified and highlighted in red
- **SC-003**: Visual indicators update immediately when due date changes or task is completed
- **SC-004**: Users can distinguish between overdue, due today, and upcoming tasks at a glance (95% accuracy)
- **SC-005**: Dashboard counts for overdue and due today tasks are accurate 100% of the time
- **SC-006**: Date/time display formats are consistent across all views
- **SC-007**: Filtering and sorting by due date works accurately with 100+ tasks

## Assumptions *(mandatory)*

1. **Timezone**: Dates stored in UTC, displayed in user's local timezone (browser timezone)
2. **Overdue Calculation**: Task is overdue if due_date < today AND task is incomplete
3. **Time-Based Indicators**: "Due today" shows for entire calendar day regardless of time
4. **Date Picker**: Using native HTML5 date input or calendar widget
5. **Time Picker**: Using native HTML5 time input with 15-minute increments
6. **No Notifications**: No email/push notifications for Phase 2 (visual indicators only)
7. **Week Definition**: "This week" means current Sunday through Saturday
8. **Midnight Edge Case**: Due time of 00:00 treated as start of day (not end of previous day)
9. **No Reminders**: No proactive reminders or alarms in Phase 2 (visual indicators only)
10. **Due Time Optional**: Most tasks will only have due date, time is for specific appointments
