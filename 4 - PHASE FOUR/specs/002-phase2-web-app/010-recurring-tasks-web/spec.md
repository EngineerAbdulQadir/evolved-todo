# Feature Specification: Recurring Tasks (Web)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Create recurring task functionality for web application allowing users to create and manage tasks that repeat on schedules (daily, weekly, monthly)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Daily Recurring Task (Priority: P3)

As a user, I want to create a task that recurs every day, so I don't have to manually create routine daily tasks.

**Why this priority**: Advanced feature useful for daily habits but not essential for basic task management.

**Independent Test**: Can be fully tested by creating a task "Daily standup" with recurrence "daily", completing it, and verifying a new incomplete instance appears for tomorrow.

**Acceptance Scenarios**:

1. **Given** I create a task "Daily standup" with recurrence "daily", **When** I complete it, **Then** a new incomplete instance is created for tomorrow with same title and details
2. **Given** I have a daily recurring task, **When** I view it, **Then** I see a repeat icon indicator
3. **Given** I complete a daily recurring task, **When** the new instance is created, **Then** it has the same description, priority, and tags as the original

---

### User Story 2 - Create Weekly Recurring Task (Priority: P3)

As a user, I want to create a task that recurs weekly on a specific day (e.g., every Monday), so I can track weekly routines.

**Why this priority**: Useful for weekly meetings and reviews but advanced feature.

**Independent Test**: Can be fully tested by creating a task "Weekly review" with recurrence "weekly on Monday", completing it, and verifying a new instance appears for next Monday.

**Acceptance Scenarios**:

1. **Given** I create a task "Weekly review" with recurrence "weekly on Monday", **When** I complete it on any day, **Then** a new instance is created for next Monday
2. **Given** I am creating a weekly recurring task, **When** I select the day, **Then** I can choose from Monday-Sunday (1-7)
3. **Given** I complete a weekly task on Thursday, **When** the next instance is created, **Then** it's scheduled for the next occurrence of the selected weekday

---

### User Story 3 - Create Monthly Recurring Task (Priority: P3)

As a user, I want to create a task that recurs monthly on a specific day (e.g., 15th of each month), so I can track monthly responsibilities.

**Why this priority**: Useful for monthly bills and reviews but less common than daily/weekly.

**Independent Test**: Can be fully tested by creating a task "Pay rent" with recurrence "monthly on 15th", completing it, and verifying a new instance appears for 15th of next month.

**Acceptance Scenarios**:

1. **Given** I create a task "Pay rent" with recurrence "monthly on 15th", **When** I complete it, **Then** a new instance is created for 15th of next month
2. **Given** I am creating a monthly recurring task, **When** I select the day, **Then** I can choose from 1-31
3. **Given** I complete a monthly task on 30th and it recurs on 15th, **When** the next instance is created, **Then** it's scheduled for 15th of next month

---

### User Story 4 - View Recurring Task Indicator (Priority: P3)

As a user, I want to see which tasks are recurring with a visual indicator, so I can distinguish them from one-time tasks.

**Why this priority**: Important for understanding task type but only relevant for users using recurring tasks.

**Independent Test**: Can be fully tested by viewing a list with recurring and non-recurring tasks, and verifying recurring tasks show a repeat icon.

**Acceptance Scenarios**:

1. **Given** I have a recurring task, **When** I view my task list, **Then** I see a repeat icon next to the task title
2. **Given** I hover over the repeat icon, **When** I see the tooltip, **Then** it shows the recurrence pattern (e.g., "Repeats daily")
3. **Given** I view task details, **When** I see recurrence info, **Then** it shows pattern and next scheduled occurrence date

---

### User Story 5 - Stop Future Recurrences (Priority: P3)

As a user, I want to stop a recurring task from creating future instances, so I can end routines I no longer need.

**Why this priority**: Essential for managing recurring tasks but only relevant for users using that feature.

**Independent Test**: Can be fully tested by removing recurrence from a recurring task and verifying no new instances are created after completion.

**Acceptance Scenarios**:

1. **Given** I have a recurring task, **When** I edit it and remove recurrence, **Then** no new instances are created when I complete it
2. **Given** I delete a recurring task, **When** it's deleted, **Then** no new instances are created in the future

---

### Edge Cases

- What happens when completing a weekly task that's due on a day that's already passed this week?
- What happens when monthly recurrence day is 31 but next month only has 30 days?
- What happens when a user completes a recurring task multiple times in one day?
- What happens when a recurring task is edited while an instance is incomplete?
- What happens when a user changes recurrence pattern on an existing recurring task?

## Requirements *(mandatory)*

### Functional Requirements

**Recurrence Creation:**
- **FR-001**: System MUST allow users to set recurrence pattern when creating tasks
- **FR-002**: Recurrence options MUST include: "daily", "weekly on [day]", "monthly on [day of month]"
- **FR-003**: For weekly recurrence, user MUST be able to select day of week (1=Monday, 7=Sunday)
- **FR-004**: For monthly recurrence, user MUST be able to select day of month (1-31)
- **FR-005**: Recurrence field MUST be optional (tasks can be non-recurring)

**Instance Creation:**
- **FR-006**: Completing a recurring task MUST automatically create new instance for next occurrence
- **FR-007**: New instance MUST be created within 1 second of marking previous instance complete
- **FR-008**: New instance MUST copy title, description, priority, tags, and recurrence pattern from original
- **FR-009**: New instance MUST be created as incomplete (not completed)
- **FR-010**: Original completed instance MUST remain in task history

**Recurrence Logic:**
- **FR-011**: Daily recurrence MUST create next instance for tomorrow
- **FR-012**: Weekly recurrence MUST create next instance for next occurrence of selected weekday
- **FR-013**: Monthly recurrence MUST create next instance for same day of next month
- **FR-014**: If monthly recurrence day exceeds days in next month (e.g., 31st but next month has 30 days), MUST create for last day of month

**Visual Indicators:**
- **FR-015**: Recurring tasks MUST show repeat icon in task list
- **FR-016**: Repeat icon tooltip MUST show recurrence pattern
- **FR-017**: Task detail view MUST show full recurrence information

**Editing & Stopping:**
- **FR-018**: Users MUST be able to edit recurrence pattern on existing tasks
- **FR-019**: Removing recurrence MUST stop future instance creation
- **FR-020**: Deleting a recurring task MUST not delete historical completed instances (only stops future instances)

**API Integration:**
- **FR-021**: Backend MUST validate recurrence pattern before saving
- **FR-022**: Backend MUST create new instance when POST /api/{user_id}/tasks/{id}/complete is called on recurring task
- **FR-023**: Backend MUST return both completed instance and new instance in response
- **FR-024**: Backend MUST calculate next occurrence date based on recurrence pattern

### Key Entities

- **Task**: Standard task entity with additional fields:
  - recurrence (nullable string: "daily", "weekly", "monthly")
  - recurrence_day (nullable integer: 1-7 for weekly, 1-31 for monthly)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New recurring instance created within 1 second of completing previous instance
- **SC-002**: 100% accuracy in next occurrence date calculation
- **SC-003**: New instances correctly copy all relevant fields from original task
- **SC-004**: Recurring tasks are visually distinguishable from one-time tasks
- **SC-005**: Users can successfully create daily, weekly, and monthly recurring tasks
- **SC-006**: Recurrence logic handles edge cases (month boundaries, leap years) correctly

## Assumptions *(mandatory)*

1. **Trigger**: New instance created only when current instance is marked complete (not time-based)
2. **Instance Limit**: No limit on number of instances that can be created from one recurring task
3. **Time Zone**: Dates calculated in user's local time zone (no UTC consideration for Phase 2)
4. **Multiple Instances**: Only one incomplete instance exists at a time (completing creates next)
5. **Recurrence UI**: Recurrence options presented as dropdown or radio buttons in task form
6. **Editing Impact**: Editing recurrence pattern only affects future instances, not completed ones
7. **Monthly Edge Case**: If recurrence day > days in next month, use last day of that month
