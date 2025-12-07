# Feature Specification: Recurring Tasks

**Feature Branch**: `009-recurring-tasks`
**Created**: 2025-12-06
**Status**: Approved
**Input**: User description: "Recurring Tasks - Auto-reschedule repeating tasks (e.g., 'weekly meeting') via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Daily Recurring Task (Priority: P1)

As a user, I want to create tasks that repeat daily, so I don't have to manually recreate routine daily tasks like "Check email" or "Review calendar".

**Why this priority**: Many tasks recur daily (morning routines, daily standup meetings, end-of-day reviews). Auto-recreation reduces manual work and ensures these tasks are never forgotten.

**Independent Test**: Can be tested by creating a daily recurring task, marking it complete, then verifying a new instance is automatically created for the next day.

**Acceptance Scenarios**:

1. **Given** I create a task "Check email" with daily recurrence, **When** I mark it complete, **Then** a new "Check email" task is created for tomorrow
2. **Given** I have a daily recurring task, **When** the next occurrence is created, **Then** it has the same title, description, and priority as the original
3. **Given** I mark a daily recurring task complete on Monday, **When** I view tasks on Tuesday, **Then** I see a new instance of that task

---

### User Story 2 - Create Weekly Recurring Task (Priority: P1)

As a user, I want to create tasks that repeat weekly, so I can manage tasks like "Team meeting every Monday" or "Weekly report due Friday".

**Why this priority**: Weekly tasks are common (meetings, reports, reviews). Weekly recurrence handles most recurring business and personal tasks.

**Independent Test**: Can be tested by creating a weekly recurring task, completing it, then verifying it recurs on the same day next week.

**Acceptance Scenarios**:

1. **Given** I create a task "Team meeting" with weekly recurrence on Monday, **When** I mark it complete, **Then** a new instance is created for next Monday
2. **Given** I have a weekly recurring task, **When** the recurrence is set for "every Friday", **Then** new instances only appear on Fridays
3. **Given** I complete a weekly task early (before its scheduled day), **When** recurrence triggers, **Then** the next instance still follows the weekly schedule

---

### User Story 3 - Create Monthly Recurring Task (Priority: P2)

As a user, I want to create tasks that repeat monthly, so I can handle tasks like "Pay rent on 1st" or "Monthly review meeting".

**Why this priority**: Monthly tasks are less frequent but important (bills, reports, reviews). Monthly recurrence reduces the need to manually track these less-frequent but critical tasks.

**Independent Test**: Can be tested by creating a monthly recurring task, completing it, then verifying it recurs in the next month.

**Acceptance Scenarios**:

1. **Given** I create a task "Pay rent" with monthly recurrence on the 1st, **When** I mark it complete, **Then** a new instance is created for next month's 1st
2. **Given** I have a monthly recurring task set for the 15th, **When** the task is completed, **Then** the next occurrence is scheduled for the 15th of the next month

---

### User Story 4 - Stop Recurring Task (Priority: P2)

As a user, I want to stop a task from recurring, so I can handle cases where a recurring task is no longer needed (e.g., project completed, routine changed).

**Why this priority**: Circumstances change. Users need to disable recurrence for tasks that are no longer relevant without deleting all future occurrences.

**Independent Test**: Can be tested by creating a recurring task, stopping its recurrence, then verifying no new instances are created after completion.

**Acceptance Scenarios**:

1. **Given** I have a recurring task, **When** I disable recurrence, **Then** marking it complete does not create a new instance
2. **Given** I stop a recurring task, **When** I view the task details, **Then** it shows as non-recurring

---

### Edge Cases

- What happens when a recurring task is deleted (stop future occurrences)?
- What happens when marking an already-rescheduled occurrence complete (create another)?
- What happens to recurring tasks with due dates (reschedule due date too)?
- How does the system handle edge dates (e.g., monthly task on 31st in months with 30 days)?
- Can a recurring task also be a one-time task (toggle recurrence on/off)?
- What happens when updating a recurring task (update future occurrences too)?
- How are recurring tasks distinguished from one-time tasks in the list?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support daily recurrence pattern (every day)
- **FR-002**: System MUST support weekly recurrence pattern (specific day of week)
- **FR-003**: System MUST support monthly recurrence pattern (specific day of month)
- **FR-004**: System MUST automatically create next occurrence when recurring task is marked complete
- **FR-005**: System MUST preserve title, description, priority, and tags in new occurrences
- **FR-006**: System MUST assign new ID and reset completion status for each occurrence
- **FR-007**: System MUST allow disabling recurrence for a task
- **FR-008**: System MUST indicate which tasks are recurring in task list view
- **FR-009**: System MUST handle edge cases (e.g., 31st of month when next month has 30 days)
- **FR-010**: System MUST not create duplicate occurrences if task is completed multiple times rapidly

### Key Entities

- **Task**: Enhanced with recurrence information
  - **New Attributes**:
    - Recurrence Pattern: Enum (none, daily, weekly, monthly)
    - Recurrence Day: Integer (for weekly: 1-7 for Mon-Sun; for monthly: 1-31)
    - Is Recurring: Boolean flag
  - **Existing Attributes**: ID, title, description, status, priority, tags (inherited by new occurrences)

- **Recurrence Patterns**:
  - Daily: Repeat every day
  - Weekly: Repeat on specific day of week (e.g., every Monday)
  - Monthly: Repeat on specific day of month (e.g., every 15th)

### Assumptions

1. **Trigger Mechanism**: New occurrence created immediately when recurring task is marked complete
2. **Occurrence Independence**: Each occurrence is a separate task with unique ID
3. **Attribute Inheritance**: New occurrences inherit title, description, priority, tags from original
4. **Status Reset**: Each new occurrence starts as incomplete
5. **Edge Date Handling**: Monthly tasks on 31st reschedule to last day of month (e.g., Feb 28/29)
6. **No Retroactive Creation**: Only future occurrences created; past missed occurrences not created
7. **Visual Indicator**: Recurring tasks show indicator like "↻" in list view

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New occurrence created within 1 second of marking recurring task complete
- **SC-002**: 100% of daily recurring tasks create next occurrence correctly
- **SC-003**: 100% of weekly recurring tasks create occurrence on correct day of week
- **SC-004**: 100% of monthly recurring tasks create occurrence on correct day of month
- **SC-005**: New occurrences inherit all attributes (title, description, priority, tags) correctly
- **SC-006**: Disabling recurrence prevents new occurrences 100% of the time
- **SC-007**: Edge date cases (e.g., Feb 31st) are handled without errors
- **SC-008**: Recurring tasks are visually distinguishable from one-time tasks
- **SC-009**: 90% of users successfully create and manage recurring tasks
- **SC-010**: No duplicate occurrences created when completing task multiple times
