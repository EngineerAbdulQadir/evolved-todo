# Feature Specification: View Tasks (Web)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Create task list dashboard view for web application displaying all user tasks with filtering, sorting, and detail views"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View All Tasks (Priority: P1)

As a user, I want to see a list of all my tasks when I log in, so I can quickly see what needs to be done.

**Why this priority**: This is the core dashboard experience. Without being able to view tasks, users cannot interact with their data. This is the central hub of the application.

**Independent Test**: Can be fully tested by logging in with an account that has 5 tasks, navigating to the dashboard, and verifying all 5 tasks are displayed with their titles, completion status, and creation dates.

**Acceptance Scenarios**:

1. **Given** I have 10 tasks in my account, **When** I log in and view my dashboard, **Then** I see all 10 tasks listed in reverse chronological order (newest first)
2. **Given** I have no tasks, **When** I view my dashboard, **Then** I see an empty state message "No tasks yet. Create your first task to get started!"
3. **Given** I am viewing my task list, **When** I see each task, **Then** I can see the task title, completion status (checkbox), and created date at minimum
4. **Given** I have 100 tasks, **When** I load my dashboard, **Then** all tasks load within 2 seconds
5. **Given** I just created a new task, **When** I return to the dashboard, **Then** I see the new task at the top of the list

---

### User Story 2 - View Task Details (Priority: P1)

As a user, I want to click on a task to see all its details (description, priority, tags, due date), so I can get full context about the task.

**Why this priority**: Essential for viewing the complete information about tasks. Users need access to descriptions and metadata they added.

**Independent Test**: Can be fully tested by clicking on a task with title "Plan meeting" that has description, priority, and tags, and verifying a detail view opens showing all fields.

**Acceptance Scenarios**:

1. **Given** I am viewing my task list, **When** I click on a task title, **Then** a detail view opens showing title, description, priority, tags, due date, recurrence, and timestamps
2. **Given** I am viewing task details, **When** I see the description, **Then** line breaks and formatting are preserved
3. **Given** I am viewing a task with no optional fields, **When** I see the details, **Then** empty fields show as "Not set" or are hidden
4. **Given** I am viewing task details, **When** I click a close button or press Escape, **Then** the detail view closes and I return to the task list
5. **Given** I am viewing task details, **When** I see tags, **Then** each tag is displayed as a clickable badge

---

### User Story 3 - View Completed vs Incomplete Tasks (Priority: P1)

As a user, I want to see which tasks are completed and which are incomplete, so I can focus on what still needs to be done.

**Why this priority**: Core task management functionality. Users need to distinguish between done and not-done tasks.

**Independent Test**: Can be fully tested by viewing a list with 3 completed and 3 incomplete tasks, and verifying that completed tasks have a checked checkbox and visual differentiation (e.g., strikethrough text or muted appearance).

**Acceptance Scenarios**:

1. **Given** I have a mix of completed and incomplete tasks, **When** I view my task list, **Then** completed tasks show with checked checkbox and strikethrough text
2. **Given** I am viewing my task list, **When** I see incomplete tasks, **Then** they have an empty checkbox and normal text styling
3. **Given** I have many completed tasks, **When** I view my list, **Then** I can easily distinguish completed from incomplete tasks visually
4. **Given** I am viewing my task list, **When** I see a completed task, **Then** it shows completion date/timestamp

---

### User Story 4 - Filter Tasks by Completion Status (Priority: P2)

As a user, I want to filter my task list to show only incomplete tasks, only completed tasks, or all tasks, so I can focus on relevant items.

**Why this priority**: Important for managing large task lists but not essential for basic viewing. Users can still see all tasks without filtering.

**Independent Test**: Can be fully tested by clicking a filter button for "Active" (incomplete) tasks and verifying only incomplete tasks are shown, then switching to "Completed" and seeing only completed tasks.

**Acceptance Scenarios**:

1. **Given** I have 10 incomplete and 5 completed tasks, **When** I click the "Active" filter, **Then** I see only the 10 incomplete tasks
2. **Given** I am viewing active tasks, **When** I click the "Completed" filter, **Then** I see only the 5 completed tasks
3. **Given** I am viewing filtered tasks, **When** I click the "All" filter, **Then** I see all 15 tasks
4. **Given** I apply a filter, **When** I refresh the page, **Then** the filter persists (stored in URL query param or localStorage)
5. **Given** I am viewing active tasks only, **When** I complete a task, **Then** it disappears from the list immediately (stays in "Completed" filter)

---

### User Story 5 - View Task Priority Indicators (Priority: P2)

As a user, I want to see priority levels visually indicated in my task list (color-coded or with icons), so I can quickly identify important tasks.

**Why this priority**: Enhances task organization but isn't essential for basic task viewing. Users can still see tasks without priority indicators.

**Independent Test**: Can be fully tested by viewing a list with tasks of different priorities and verifying that high priority tasks show red indicator, medium shows yellow, and low shows green.

**Acceptance Scenarios**:

1. **Given** I have tasks with different priorities, **When** I view my task list, **Then** high priority tasks show red badge/indicator, medium show yellow, low show green
2. **Given** I am viewing my task list, **When** I see a task with no priority, **Then** it shows no priority indicator
3. **Given** I have many high priority tasks, **When** I view my list, **Then** I can quickly scan for red indicators to find urgent items

---

### User Story 6 - View Task Tags (Priority: P2)

As a user, I want to see tags displayed on each task in the list view, so I can understand task categorization at a glance.

**Why this priority**: Useful for organization but not critical for basic task viewing. Tags enhance but don't block core functionality.

**Independent Test**: Can be fully tested by viewing a task with tags "work, urgent, meeting" and verifying the tags appear as individual badges below or next to the task title.

**Acceptance Scenarios**:

1. **Given** I have a task with tags "work, urgent, meeting", **When** I view the task in my list, **Then** I see three separate tag badges
2. **Given** I am viewing task tags, **When** I click on a tag badge, **Then** the list filters to show only tasks with that tag
3. **Given** I am viewing my task list, **When** I see tasks without tags, **Then** no tag badges are shown

---

### User Story 7 - View Due Date Indicators (Priority: P2)

As a user, I want to see due dates on tasks in the list view with visual indicators for overdue and upcoming tasks, so I can prioritize time-sensitive work.

**Why this priority**: Important for deadline tracking but not essential for all tasks. Many tasks don't have due dates.

**Independent Test**: Can be fully tested by viewing a list with tasks due today, tomorrow, and in the past, and verifying each shows appropriate visual indicator (red for overdue, yellow for due today, normal for future).

**Acceptance Scenarios**:

1. **Given** I have a task due today, **When** I view my task list, **Then** I see "Due today" in yellow/orange highlighting
2. **Given** I have an overdue task, **When** I view my task list, **Then** I see "Overdue" in red highlighting
3. **Given** I have a task due tomorrow, **When** I view my task list, **Then** I see "Due tomorrow" with clock icon
4. **Given** I have a task due in 7 days, **When** I view my task list, **Then** I see the formatted due date "Due Dec 17, 2025"
5. **Given** I have tasks without due dates, **When** I view my task list, **Then** no due date indicator is shown

---

### User Story 8 - View Recurring Task Indicators (Priority: P3)

As a user, I want to see which tasks are recurring with a visual indicator (icon), so I can distinguish one-time from repeating tasks.

**Why this priority**: Advanced feature that's only relevant for users using recurring tasks. Not essential for basic viewing.

**Independent Test**: Can be fully tested by viewing a list with 2 recurring tasks and 3 one-time tasks, and verifying the recurring tasks show a repeat icon.

**Acceptance Scenarios**:

1. **Given** I have a recurring task, **When** I view my task list, **Then** I see a repeat icon next to the task title
2. **Given** I hover over the repeat icon, **When** I see the tooltip, **Then** it shows the recurrence pattern (e.g., "Repeats daily")
3. **Given** I am viewing task details for a recurring task, **When** I see the recurrence information, **Then** it shows pattern and next occurrence date

---

### User Story 9 - Responsive Mobile View (Priority: P2)

As a user on mobile, I want the task list to be readable and usable on my phone screen, so I can manage tasks on the go.

**Why this priority**: Important for modern web applications but not blocking for desktop users. Mobile optimization can come after core desktop functionality.

**Independent Test**: Can be fully tested by opening the dashboard on a mobile device (or mobile viewport in dev tools), viewing the task list, and verifying tasks are readable, checkboxes are tappable, and the layout adapts to narrow screen.

**Acceptance Scenarios**:

1. **Given** I am viewing the dashboard on mobile, **When** I see my task list, **Then** tasks stack vertically with full width
2. **Given** I am on mobile, **When** I tap a task, **Then** the detail view opens in a full-screen modal
3. **Given** I am on mobile, **When** I see task metadata (priority, tags, due date), **Then** it's displayed in a condensed, readable format
4. **Given** I am on mobile, **When** I tap the checkbox to complete a task, **Then** the tap target is large enough (44x44px minimum)

---

### Edge Cases

- What happens when a user has 1000+ tasks in their account?
- What happens when a task title is extremely long (approaching 200 character limit)?
- What happens when a task description contains special characters or HTML?
- What happens when the API request to fetch tasks fails?
- What happens when a user is viewing task details and another user updates that task?
- What happens when a user has tasks with emojis in the title?
- What happens when the task list is loading (slow network)?
- What happens when a user applies multiple filters simultaneously (completed + high priority)?

## Requirements *(mandatory)*

### Functional Requirements

**Task List Display:**
- **FR-001**: System MUST display all tasks belonging to the authenticated user on the dashboard
- **FR-002**: Tasks MUST be displayed in reverse chronological order by default (newest first)
- **FR-003**: Each task in the list MUST show title, completion checkbox, and created timestamp at minimum
- **FR-004**: System MUST show empty state message when user has no tasks
- **FR-005**: Task list MUST update in real-time when tasks are added, updated, or deleted

**Task Details View:**
- **FR-006**: System MUST provide a way to view full task details (click on task or dedicated button)
- **FR-007**: Task detail view MUST show all fields: title, description, completion status, priority, tags, due date, due time, recurrence, created timestamp, updated timestamp
- **FR-008**: System MUST preserve formatting (line breaks) in task description when displaying
- **FR-009**: Task detail view MUST be closable (close button, Escape key, click outside)
- **FR-010**: Empty optional fields MUST show as "Not set" or be hidden in detail view

**Completion Status Display:**
- **FR-011**: Completed tasks MUST show with checked checkbox and visual differentiation (strikethrough text)
- **FR-012**: Incomplete tasks MUST show with empty checkbox and normal text styling
- **FR-013**: System MUST show completion timestamp for completed tasks
- **FR-014**: Checkbox MUST be interactive (clicking toggles completion status)

**Filtering:**
- **FR-015**: System MUST provide filter options: "All", "Active" (incomplete), "Completed"
- **FR-016**: Applying "Active" filter MUST show only incomplete tasks
- **FR-017**: Applying "Completed" filter MUST show only completed tasks
- **FR-018**: Applied filter MUST persist across page refreshes (localStorage or URL query param)
- **FR-019**: Completing a task while viewing "Active" filter MUST remove it from view immediately

**Priority Display:**
- **FR-020**: High priority tasks MUST show red badge/indicator
- **FR-021**: Medium priority tasks MUST show yellow badge/indicator
- **FR-022**: Low priority tasks MUST show green badge/indicator
- **FR-023**: Tasks with no priority MUST show no priority indicator

**Tag Display:**
- **FR-024**: Tags MUST be displayed as individual badges in task list view
- **FR-025**: Clicking a tag badge MUST filter the task list to show only tasks with that tag
- **FR-026**: Tags MUST be visually distinct and readable

**Due Date Display:**
- **FR-027**: Tasks due today MUST show "Due today" with yellow/orange highlighting
- **FR-028**: Overdue tasks (due date in past, task incomplete) MUST show "Overdue" with red highlighting
- **FR-029**: Tasks due tomorrow MUST show "Due tomorrow" with clock icon
- **FR-030**: Future due dates MUST show formatted date (e.g., "Due Dec 17, 2025")
- **FR-031**: Tasks without due dates MUST show no due date indicator
- **FR-032**: System MUST display due time if set (e.g., "Due today at 2:00 PM")

**Recurring Task Display:**
- **FR-033**: Recurring tasks MUST show repeat icon indicator
- **FR-034**: Hovering/tapping repeat icon MUST show tooltip with recurrence pattern
- **FR-035**: Task detail view MUST show full recurrence information (pattern, next occurrence)

**Performance & Loading:**
- **FR-036**: Task list MUST show loading skeleton/spinner while fetching data
- **FR-037**: System MUST handle pagination or virtual scrolling for 100+ tasks
- **FR-038**: Task list MUST load within 2 seconds for up to 100 tasks

**Responsive Design:**
- **FR-039**: Task list MUST be responsive and readable on mobile devices (320px+ width)
- **FR-040**: Mobile task detail view MUST open as full-screen modal
- **FR-041**: Tap targets (checkboxes, buttons) MUST meet 44x44px minimum size on mobile
- **FR-042**: Layout MUST adapt to narrow screens (single column, stacked elements)

**API Integration:**
- **FR-043**: Frontend MUST send GET request to /api/{user_id}/tasks to fetch all tasks
- **FR-044**: Backend MUST return only tasks belonging to the authenticated user (filtered by user_id from JWT)
- **FR-045**: Backend MUST return tasks as JSON array with all fields
- **FR-046**: Backend MUST return 200 OK with task array on success
- **FR-047**: Backend MUST return 401 Unauthorized if JWT token is invalid

### Key Entities

- **Task**: Represents a todo item that users want to track and complete
  - All fields as defined in Add Task spec
  - Displayed fields: title, description, completion status, priority, tags, due date, due time, recurrence, created timestamp, updated timestamp

- **Task List View State**: Client-side state for managing task list display
  - Current filter (all/active/completed)
  - Selected task for detail view
  - Loading state
  - Error state

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Performance:**
- **SC-001**: Dashboard with 100 tasks loads within 2 seconds on 3G connection
- **SC-002**: Task list renders within 500ms after data is fetched
- **SC-003**: Task detail view opens within 200ms of clicking task
- **SC-004**: Filter changes apply within 100ms

**Data Accuracy:**
- **SC-005**: 100% of user's tasks are displayed in the list (no missing tasks)
- **SC-006**: Task data displayed matches database state with 100% accuracy
- **SC-007**: Real-time updates reflect within 1 second of changes (optimistic UI updates)

**Visual Clarity:**
- **SC-008**: 90% of users can distinguish completed from incomplete tasks at a glance
- **SC-009**: Priority indicators are visible and understandable without explanation
- **SC-010**: Overdue tasks are immediately noticeable (95% of users identify them correctly)

**User Experience:**
- **SC-011**: Empty state message helps 100% of new users understand how to create first task
- **SC-012**: Task detail view shows all relevant information without scrolling on desktop (1920x1080)
- **SC-013**: Users can complete/uncomplete tasks in under 1 second (single checkbox click)
- **SC-014**: 95% of users successfully filter their task list on first attempt

**Responsive Design:**
- **SC-015**: Task list is fully functional on screen widths from 320px to 2560px
- **SC-016**: All interactive elements meet accessibility tap target sizes on mobile
- **SC-017**: Mobile layout is usable and readable without zooming required

**Reliability:**
- **SC-018**: API failures show user-friendly error message with retry option
- **SC-019**: Task list gracefully handles edge cases (1000+ tasks, very long titles, special characters)
- **SC-020**: 99.9% uptime for task viewing functionality

## Assumptions *(mandatory)*

1. **Default View**: Dashboard shows all tasks by default (no filter applied)
2. **Sorting**: Tasks sorted by created timestamp descending (newest first) unless user applies different sort
3. **Pagination**: For Phase 2, fetch all tasks at once (pagination added later if needed for 1000+ tasks)
4. **Real-time Updates**: No WebSocket push notifications in Phase 2 (updates visible on page refresh or after user action)
5. **Task Detail UI**: Detail view can be modal/drawer/dedicated page (to be determined during planning)
6. **Empty State**: Empty state shows for both "no tasks at all" and "no tasks matching filter"
7. **Checkbox Behavior**: Clicking checkbox immediately sends API request to toggle completion (optimistic UI update)
8. **Tag Filtering**: Clicking a tag shows tasks with that exact tag match (no partial matching)
9. **Mobile Breakpoint**: Mobile layout activates at 768px width and below
10. **Loading State**: Show skeleton loaders or spinner while fetching tasks (avoid blank screen)
