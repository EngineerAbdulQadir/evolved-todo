# Feature Specification: Add Task (Web)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Create task creation interface for web application allowing users to add new tasks with title, description, priority, tags, due date, and recurrence options"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Task with Title Only (Priority: P1)

As a user, I want to create a new task by providing just a title, so I can quickly capture tasks without needing to add extra details.

**Why this priority**: This is the absolute minimum viable functionality. Users need to be able to create tasks with minimal friction. Every other feature builds on this foundation.

**Independent Test**: Can be fully tested by clicking the "Add Task" button, entering a title "Buy groceries" in the input field, submitting the form, and verifying the task appears in the task list with only the title populated.

**Acceptance Scenarios**:

1. **Given** I am logged in and viewing my dashboard, **When** I click "Add Task" button and enter title "Buy groceries" and click "Save", **Then** a new task is created and appears at the top of my task list
2. **Given** I am on the add task form, **When** I enter a title and press Enter key, **Then** the task is created (keyboard shortcut works)
3. **Given** I am on the add task form, **When** I try to submit with empty title, **Then** I see error message "Title is required" and task is not created
4. **Given** I just created a task, **When** the task appears in my list, **Then** it shows as incomplete (unchecked) by default
5. **Given** I created a task with only title, **When** I view the task details, **Then** all optional fields (description, priority, tags, due date, recurrence) are empty/null

---

### User Story 2 - Create Task with Title and Description (Priority: P1)

As a user, I want to add a description to my task, so I can capture more context and details about what needs to be done.

**Why this priority**: Descriptions provide essential context for tasks. This is a core feature that users expect immediately after basic title-only creation.

**Independent Test**: Can be fully tested by creating a new task with title "Plan meeting" and description "Schedule with team to discuss Q1 goals", submitting it, and verifying both fields are saved and displayed in the task list and detail view.

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I enter title "Plan meeting" and description "Schedule with team to discuss Q1 goals" and click Save, **Then** both title and description are saved and visible in task details
2. **Given** I am adding a task, **When** I enter a very long description (1000 characters), **Then** the description is saved successfully
3. **Given** I am adding a task with description, **When** I use line breaks in the description text area, **Then** the formatting is preserved when viewing the task
4. **Given** I am on the add task form, **When** I leave description empty, **Then** the task is still created successfully (description is optional)

---

### User Story 3 - Create Task with Priority (Priority: P2)

As a user, I want to assign a priority level (low, medium, high) to my task when creating it, so I can organize my tasks by importance.

**Why this priority**: Priority is an intermediate feature that enhances task organization but isn't essential for basic task creation.

**Independent Test**: Can be fully tested by creating a task with title "Fix bug" and selecting priority "high" from a dropdown, submitting it, and verifying the task displays with a high priority indicator (e.g., red badge or icon).

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I select priority "high" from the dropdown and save the task, **Then** the task displays with a high priority indicator in the task list
2. **Given** I am creating a task, **When** I don't select any priority, **Then** the task is created with no priority (null/empty)
3. **Given** I am on the add task form, **When** I see the priority dropdown, **Then** I see three options: "low", "medium", "high"
4. **Given** I created a task with high priority, **When** I view my task list, **Then** I can visually distinguish high priority tasks from others (different color/icon)

---

### User Story 4 - Create Task with Tags (Priority: P2)

As a user, I want to add tags to my task when creating it, so I can categorize and group related tasks together.

**Why this priority**: Tags are useful for organization but not critical for basic task management. Users can start without tags and add this feature later.

**Independent Test**: Can be fully tested by creating a task with title "Research tools" and adding tags "work, research, tech", submitting it, and verifying the tags appear as clickable badges on the task in the list view.

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I enter tags "work, research, tech" in the tags input field and save, **Then** the task displays with three separate tag badges
2. **Given** I am adding tags, **When** I type a comma or press Enter after each tag, **Then** each tag is added as a separate badge
3. **Given** I am on the add task form, **When** I don't add any tags, **Then** the task is created successfully without tags
4. **Given** I am entering tags, **When** I type "work" and there's already a task with tag "work", **Then** I see an autocomplete suggestion for "work"

---

### User Story 5 - Create Task with Due Date (Priority: P2)

As a user, I want to set a due date for my task when creating it, so I can track deadlines and time-sensitive tasks.

**Why this priority**: Due dates are important for time management but not essential for all tasks. Many tasks don't have specific deadlines.

**Independent Test**: Can be fully tested by creating a task with title "Submit report" and setting due date to "2025-12-15", submitting it, and verifying the task displays with the due date and shows visual indicators for upcoming/overdue dates.

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I select due date "2025-12-15" from the date picker and save, **Then** the task displays with the formatted due date "Dec 15, 2025"
2. **Given** I am setting a due date, **When** I select today's date, **Then** the task shows "Due today" with special highlighting
3. **Given** I am on the add task form, **When** I don't set a due date, **Then** the task is created without a due date (optional field)
4. **Given** I set a due date in the past, **When** the task is saved, **Then** the task immediately shows as "Overdue" with red highlighting

---

### User Story 6 - Create Task with Due Time (Priority: P3)

As a user, I want to set a specific time for my due date, so I can track tasks that need to be completed at particular times.

**Why this priority**: Advanced feature that's only useful for time-sensitive tasks. Most users will only need dates, not specific times.

**Independent Test**: Can be fully tested by creating a task with title "Team standup" and setting due date "2025-12-11" with time "09:00", submitting it, and verifying the task displays with both date and time.

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I set due date "2025-12-11" and time "09:00" and save, **Then** the task displays "Due Dec 11, 2025 at 9:00 AM"
2. **Given** I set a due date, **When** I don't set a time, **Then** the task is saved with just the date (time is optional)
3. **Given** I am setting due time, **When** I use the time picker, **Then** I can select hours and minutes in 15-minute increments

---

### User Story 7 - Create Recurring Task (Priority: P3)

As a user, I want to create a task that recurs on a schedule (daily, weekly, monthly), so I don't have to manually recreate repetitive tasks.

**Why this priority**: Advanced feature useful for routine tasks but not essential for basic task management. Many users don't need recurring tasks.

**Independent Test**: Can be fully tested by creating a task with title "Weekly review" and setting recurrence to "weekly on Monday", saving it, completing the task, and verifying a new instance is automatically created for the next Monday.

**Acceptance Scenarios**:

1. **Given** I am on the add task form, **When** I select recurrence "daily" and save, **Then** the task displays with a recurrence indicator (e.g., repeat icon)
2. **Given** I create a weekly recurring task for Monday, **When** I complete the task, **Then** a new incomplete instance is created for next Monday
3. **Given** I am creating a recurring task, **When** I select "monthly", **Then** I can choose a specific day of the month (1-31)
4. **Given** I am on the add task form, **When** I don't select any recurrence, **Then** the task is created as a one-time task (non-recurring)

---

### Edge Cases

- What happens when a user tries to create a task with a title longer than 200 characters?
- What happens when a user tries to create a task with a description longer than 1000 characters?
- What happens when a user closes the add task form without saving?
- What happens when network fails while submitting a new task?
- What happens when a user tries to set a due date with invalid format?
- What happens when a user tries to create multiple tasks rapidly (double-clicking Save button)?
- What happens when a user tries to add duplicate tags to the same task?
- What happens when creating a recurring task with due date in the past?

## Requirements *(mandatory)*

### Functional Requirements

**Task Creation - Title:**
- **FR-001**: System MUST allow users to create tasks with a title
- **FR-002**: Title field MUST be required (cannot be empty)
- **FR-003**: Title MUST have maximum length of 200 characters
- **FR-004**: System MUST trim leading/trailing whitespace from title before saving

**Task Creation - Description:**
- **FR-005**: System MUST allow users to optionally add a description to tasks
- **FR-006**: Description field MUST be optional (can be empty/null)
- **FR-007**: Description MUST have maximum length of 1000 characters
- **FR-008**: System MUST preserve line breaks in description text

**Task Creation - Priority:**
- **FR-009**: System MUST allow users to optionally assign priority (low, medium, high) when creating tasks
- **FR-010**: Priority MUST be one of three values: "low", "medium", "high", or null
- **FR-011**: System MUST display priority as visual indicator (color-coded badge or icon) in task list

**Task Creation - Tags:**
- **FR-012**: System MUST allow users to optionally add tags when creating tasks
- **FR-013**: Tags MUST be stored as comma-separated string
- **FR-014**: System MUST display tags as individual clickable badges in task list
- **FR-015**: System MUST provide tag autocomplete based on existing tags from user's other tasks

**Task Creation - Due Date:**
- **FR-016**: System MUST allow users to optionally set a due date when creating tasks
- **FR-017**: Due date MUST be a valid date (ISO 8601 format: YYYY-MM-DD)
- **FR-018**: System MUST display due dates in user-friendly format (e.g., "Dec 15, 2025")
- **FR-019**: System MUST highlight overdue tasks (due date in the past and task incomplete)
- **FR-020**: System MUST highlight tasks due today with special indicator

**Task Creation - Due Time:**
- **FR-021**: System MUST allow users to optionally set a specific time for due date
- **FR-022**: Due time MUST be a valid time (HH:MM format, 24-hour)
- **FR-023**: Due time can only be set if due date is also set
- **FR-024**: System MUST display due time in 12-hour format with AM/PM

**Task Creation - Recurrence:**
- **FR-025**: System MUST allow users to optionally set recurrence pattern (daily, weekly, monthly)
- **FR-026**: For weekly recurrence, user MUST be able to specify day of week (1=Monday, 7=Sunday)
- **FR-027**: For monthly recurrence, user MUST be able to specify day of month (1-31)
- **FR-028**: System MUST display recurrence indicator icon on recurring tasks

**Form Behavior:**
- **FR-029**: Add task form MUST be accessible via "Add Task" button on dashboard
- **FR-030**: Form MUST support keyboard shortcuts (Enter to submit, Escape to cancel)
- **FR-031**: Form MUST show real-time validation errors for invalid input
- **FR-032**: Form MUST clear all fields after successful task creation
- **FR-033**: System MUST show success message after task is created

**API Integration:**
- **FR-034**: Frontend MUST send POST request to /api/{user_id}/tasks with task data
- **FR-035**: Backend MUST validate all required fields before saving
- **FR-036**: Backend MUST return 201 Created with new task object on success
- **FR-037**: Backend MUST return 400 Bad Request with validation errors on failure
- **FR-038**: Backend MUST extract user_id from JWT token to associate task with correct user

### Key Entities

- **Task**: Represents a todo item that users want to track and complete
  - Unique identifier (auto-increment integer)
  - User identifier (foreign key to User)
  - Title (required, max 200 characters)
  - Description (optional, max 1000 characters)
  - Completion status (boolean, default false)
  - Priority (optional, enum: low/medium/high)
  - Tags (optional, comma-separated string)
  - Due date (optional, ISO date)
  - Due time (optional, HH:MM format)
  - Recurrence pattern (optional, enum: daily/weekly/monthly)
  - Recurrence day (optional, integer 1-31 for monthly, 1-7 for weekly)
  - Created timestamp (auto-generated)
  - Updated timestamp (auto-updated)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Task Creation Speed:**
- **SC-001**: Users can create a simple task (title only) in under 5 seconds from clicking "Add Task" to seeing it in the list
- **SC-002**: Users can create a complex task (all fields) in under 30 seconds

**Form Validation:**
- **SC-003**: 100% of invalid submissions (empty title) are prevented with clear error message
- **SC-004**: Form validation feedback appears within 200ms of user input
- **SC-005**: 95% of users successfully create their first task without errors

**Data Integrity:**
- **SC-006**: 100% of tasks with valid data are successfully stored in database and retrievable
- **SC-007**: 0% data loss during task creation (all submitted data persists)
- **SC-008**: Character limits (200 for title, 1000 for description) are enforced 100% of the time

**User Experience:**
- **SC-009**: Task appears in list within 500ms after clicking Save
- **SC-010**: Form clears and resets within 200ms after successful submission
- **SC-011**: Success message displays for 3 seconds after task creation
- **SC-012**: Users can create multiple tasks rapidly without UI lag (5 tasks in 30 seconds)

**Recurrence & Advanced Features:**
- **SC-013**: Recurring task instances are created automatically within 1 second of completing previous instance
- **SC-014**: Due date picker allows selection of any date from today to 1 year in future
- **SC-015**: Tag autocomplete suggestions appear within 100ms of typing

**API Performance:**
- **SC-016**: POST /api/{user_id}/tasks responds within 300ms under normal load
- **SC-017**: 99% of task creation API requests succeed on first attempt
- **SC-018**: System handles 100 concurrent task creations without degradation

## Assumptions *(mandatory)*

1. **Form UI**: Add task form can be a modal/dialog or a dedicated page (to be determined during planning)
2. **Default Values**: New tasks default to incomplete status, no priority, no tags, no due date, no recurrence
3. **Task Ordering**: Newly created tasks appear at the top of the task list (newest first)
4. **Tag Format**: Tags are stored as comma-separated string in database (not separate Tag entity for Phase 2)
5. **Date/Time Input**: Using native HTML5 date and time pickers (no third-party date library required)
6. **Recurrence Trigger**: Recurring task instances created only when current instance is marked complete (not time-based)
7. **Validation**: Client-side validation for UX, server-side validation for security (both implemented)
8. **Error Handling**: Network errors during task creation show retry option
9. **Character Counting**: No character counter shown to user (limits enforced silently)
10. **Multi-field Validation**: All fields validated independently (partial form submission not allowed)
