# Feature Specification: Due Dates & Reminders

**Feature Branch**: `010-due-dates-reminders`
**Created**: 2025-12-06
**Status**: Approved
**Input**: User description: "Due Dates & Time Reminders - Set deadlines with date/time; display notifications via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Due Date for Task (Priority: P1)

As a user, I want to assign due dates to tasks, so I can track deadlines and prioritize time-sensitive work.

**Why this priority**: Many tasks have deadlines. Due dates enable time-based prioritization, help prevent missed deadlines, and provide urgency context for task planning.

**Independent Test**: Can be tested by creating a task with a due date, then viewing it to verify the due date is stored and displayed correctly.

**Acceptance Scenarios**:

1. **Given** I create a task "Submit report", **When** I set due date to "2025-12-15", **Then** the task shows due date as "Dec 15, 2025"
2. **Given** I have a task with a due date, **When** I view the task list, **Then** the due date is clearly displayed next to the task
3. **Given** I create a task without a due date, **When** I view it, **Then** it shows as "No due date" or similar indicator

---

### User Story 2 - Update/Remove Due Date (Priority: P2)

As a user, I want to change or remove a task's due date, so I can adapt to changing deadlines or remove dates from tasks that no longer have time constraints.

**Why this priority**: Deadlines change. Users need flexibility to update or remove due dates as circumstances change, without recreating tasks.

**Independent Test**: Can be tested by setting a due date, changing it to a new date, then verifying the update; and by removing a due date entirely.

**Acceptance Scenarios**:

1. **Given** I have a task with due date "2025-12-15", **When** I update it to "2025-12-20", **Then** the due date changes to the new date
2. **Given** I have a task with a due date, **When** I remove the due date, **Then** the task shows as having no due date

---

### User Story 3 - View Overdue Tasks (Priority: P1)

As a user, I want to see which tasks are overdue (due date has passed), so I can identify and address late tasks immediately.

**Why this priority**: Overdue tasks represent missed deadlines and require urgent attention. Visual indicators for overdue status help users prioritize catching up on late work.

**Independent Test**: Can be tested by creating a task with a past due date, then viewing the list to verify it's marked as overdue.

**Acceptance Scenarios**:

1. **Given** I have a task with due date "2025-12-01" and today is "2025-12-06", **When** I view the task list, **Then** the task is marked as overdue (e.g., red text, "OVERDUE" label)
2. **Given** I have both overdue and upcoming tasks, **When** I view the list, **Then** overdue tasks are visually distinct
3. **Given** I complete an overdue task, **When** I view completed tasks, **Then** it no longer shows as overdue

---

### User Story 4 - Set Reminder Time (Priority: P2)

As a user, I want to set a specific time for task reminders (not just date), so I can be reminded at the exact time I need to start the task.

**Why this priority**: Some tasks require time-specific action (meetings at 2 PM, calls at 10 AM). Time-based reminders provide more precise notifications than date-only reminders.

**Independent Test**: Can be tested by setting a due date with specific time, then verifying the time is stored and displayed.

**Acceptance Scenarios**:

1. **Given** I create a task "Team meeting", **When** I set due date to "2025-12-10 2:00 PM", **Then** the task shows both date and time
2. **Given** I have a task with due time "2:00 PM", **When** I view the task, **Then** the time is clearly displayed alongside the date

---

### User Story 5 - Receive CLI Notifications (Priority: P3)

As a user, I want to receive text-based reminders in the CLI when viewing tasks, so I'm alerted to upcoming and overdue tasks.

**Why this priority**: Active notifications help users remember important tasks. CLI-based notifications (when listing tasks) provide reminders without requiring external notification systems.

**Independent Test**: Can be tested by viewing task list with upcoming/overdue tasks and verifying reminder messages are displayed.

**Acceptance Scenarios**:

1. **Given** I have a task due today, **When** I view the task list, **Then** I see a notification like "⚠️ Task 'X' is due today"
2. **Given** I have an overdue task, **When** I view the task list, **Then** I see a notification like "🚨 Task 'Y' is overdue"
3. **Given** I have a task due tomorrow, **When** I view the list, **Then** I see a notification like "📅 Task 'Z' is due tomorrow"

---

### Edge Cases

- What happens when setting an invalid due date (e.g., "2025-13-45")?
- What happens when setting a due date in the past (during creation)?
- What happens when due time is set without a due date?
- How does the system handle timezone differences (if applicable)?
- What happens when a task becomes overdue while the app is not running?
- How are tasks due "today" distinguished from tasks due "in 1 hour"?
- What happens when filtering/sorting by due date with null values (no due date)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow assigning due date when creating a task
- **FR-002**: System MUST allow assigning due date to existing tasks
- **FR-003**: System MUST allow updating or removing due dates
- **FR-004**: System MUST support date format (YYYY-MM-DD) or natural language (e.g., "tomorrow", "next Monday")
- **FR-005**: System MUST support optional time specification (HH:MM format, 24-hour or 12-hour with AM/PM)
- **FR-006**: System MUST validate due date and time values
- **FR-007**: System MUST identify and mark overdue tasks (due date before current date)
- **FR-008**: System MUST display due dates and times clearly in task list view
- **FR-009**: System MUST provide visual distinction for overdue tasks (e.g., color, indicator)
- **FR-010**: System MUST display reminder notifications when viewing tasks (upcoming, due today, overdue)
- **FR-011**: System MUST allow filtering tasks by due date (overdue, today, this week, no due date)
- **FR-012**: System MUST allow sorting tasks by due date (earliest first, latest first)

### Key Entities

- **Task**: Enhanced with due date and reminder attributes
  - **New Attributes**:
    - Due Date: Date (YYYY-MM-DD format) - optional
    - Due Time: Time (HH:MM format) - optional
    - Is Overdue: Computed boolean (true if due date < current date and status = incomplete)
  - **Existing Attributes**: ID, title, description, status, priority, tags

- **Due Date Status**:
  - Overdue: Due date in the past, task incomplete
  - Due Today: Due date is current date
  - Upcoming: Due date in future
  - No Due Date: Task has no deadline

### Assumptions

1. **Date Format**: Accept ISO format (YYYY-MM-DD) and natural language ("tomorrow", "Dec 15")
2. **Time Format**: Optional time in HH:MM format (24-hour) or with AM/PM (12-hour)
3. **Overdue Calculation**: Computed on-the-fly when viewing tasks (not stored)
4. **Timezone**: Use local system timezone for all date/time operations
5. **Notifications**: Display reminders as text in CLI output (not OS-level notifications in Phase 1)
6. **Default Time**: If no time specified, assume end of day (23:59) for due date comparisons
7. **Visual Indicators**: Use text-based indicators (🚨 overdue, ⚠️ due today, 📅 upcoming)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can set due dates in under 3 seconds
- **SC-002**: 100% of tasks with due dates display date correctly
- **SC-003**: 100% of tasks with due times display time correctly
- **SC-004**: Overdue tasks are correctly identified 100% of the time
- **SC-005**: Overdue tasks are visually distinct from non-overdue tasks 100% of the time
- **SC-006**: Invalid due dates are rejected with clear error messages
- **SC-007**: Users see reminder notifications for due/overdue tasks when viewing list
- **SC-008**: Filtering by due date status (overdue, today, this week) works correctly
- **SC-009**: Sorting by due date displays tasks in chronological order
- **SC-010**: 95% of users understand overdue status indicators without documentation
