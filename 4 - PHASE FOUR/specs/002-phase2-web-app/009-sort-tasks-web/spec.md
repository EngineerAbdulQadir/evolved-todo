# Feature Specification: Sort Tasks (Web)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Create sorting interface for web application allowing users to sort tasks by various criteria (date, priority, title, completion status)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sort by Created Date (Priority: P2)

As a user, I want to sort my task list by creation date (newest or oldest first), so I can see recently added tasks or find old tasks.

**Why this priority**: Important for managing task list organization, provides temporal context.

**Independent Test**: Can be fully tested by selecting "Sort by: Newest First" and verifying tasks appear in reverse chronological order, then selecting "Oldest First" and verifying order reverses.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Newest First", **When** I view my tasks, **Then** tasks appear with most recently created at the top
2. **Given** I select "Sort by: Oldest First", **When** I view my tasks, **Then** tasks appear with oldest created at the top
3. **Given** I change sort order, **When** I refresh the page, **Then** sort order persists

---

### User Story 2 - Sort by Priority (Priority: P2)

As a user, I want to sort tasks by priority level, so I can focus on the most important tasks first.

**Why this priority**: Essential for priority-based workflow, helps users focus on urgent work.

**Independent Test**: Can be fully tested by selecting "Sort by: Priority" and verifying high priority tasks appear first, followed by medium, then low, then no priority.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Priority", **When** I view my tasks, **Then** high priority tasks appear first, then medium, then low, then no priority
2. **Given** I sort by priority, **When** tasks have same priority, **Then** they are sub-sorted by created date (newest first)

---

### User Story 3 - Sort by Due Date (Priority: P2)

As a user, I want to sort tasks by due date, so I can see which tasks are due soonest and prioritize deadline-driven work.

**Why this priority**: Critical for deadline management, helps users avoid missing due dates.

**Independent Test**: Can be fully tested by selecting "Sort by: Due Date" and verifying tasks appear with earliest due date first, with tasks without due dates at the end.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Due Date", **When** I view my tasks, **Then** tasks with earliest due dates appear first
2. **Given** I sort by due date, **When** tasks have no due date, **Then** they appear at the end of the list
3. **Given** I sort by due date, **When** tasks are overdue, **Then** they appear at the very top with special highlighting

---

### User Story 4 - Sort by Title (Alphabetical) (Priority: P3)

As a user, I want to sort tasks alphabetically by title, so I can find tasks by name quickly.

**Why this priority**: Nice to have for organization but less commonly used than date/priority sorting.

**Independent Test**: Can be fully tested by selecting "Sort by: Title (A-Z)" and verifying tasks appear in alphabetical order, then selecting "Title (Z-A)" for reverse order.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Title (A-Z)", **When** I view my tasks, **Then** tasks appear in alphabetical order by title
2. **Given** I select "Sort by: Title (Z-A)", **When** I view my tasks, **Then** tasks appear in reverse alphabetical order

---

### User Story 5 - Sort by Completion Status (Priority: P3)

As a user, I want to sort tasks to show all incomplete tasks first, then completed tasks, so I can focus on what needs to be done.

**Why this priority**: Useful but can be achieved with completion status filter, lower priority for sorting.

**Independent Test**: Can be fully tested by selecting "Sort by: Status" and verifying incomplete tasks appear first, followed by completed tasks.

**Acceptance Scenarios**:

1. **Given** I select "Sort by: Status", **When** I view my tasks, **Then** all incomplete tasks appear first, then completed tasks
2. **Given** I sort by status, **When** tasks have same status, **Then** they are sub-sorted by created date

---

### Edge Cases

- What happens when all tasks have the same sort value (e.g., all same priority)?
- What happens when sort criteria is changed while filters are active?
- What happens when a task's sortable field is updated (e.g., priority changed)?
- What happens when sorting tasks with null/empty values (no priority, no due date)?

## Requirements *(mandatory)*

### Functional Requirements

**Sort Interface:**
- **FR-001**: System MUST provide sort dropdown or buttons above task list
- **FR-002**: Sort options MUST include: "Newest First", "Oldest First", "Priority", "Due Date", "Title (A-Z)", "Title (Z-A)", "Status"
- **FR-003**: Currently active sort MUST be clearly indicated in UI
- **FR-004**: Sort order MUST persist across page refreshes (localStorage or URL param)

**Sort Behavior:**
- **FR-005**: Changing sort order MUST update task list within 200ms
- **FR-006**: Sort MUST work in combination with filters (sort filtered results)
- **FR-007**: Default sort MUST be "Newest First" (reverse chronological by created date)

**Sort Logic:**
- **FR-008**: "Priority" sort order MUST be: High → Medium → Low → No Priority
- **FR-009**: "Due Date" sort MUST put overdue tasks first, then soonest due dates, then no due date last
- **FR-010**: Tasks with equal sort values MUST use created date as secondary sort (newest first)
- **FR-011**: "Status" sort order MUST be: Incomplete → Completed
- **FR-012**: Alphabetical sort MUST be case-insensitive

**Visual Feedback:**
- **FR-013**: Sort dropdown MUST show current sort option clearly
- **FR-014**: System MUST show sort indicator (arrow up/down) for ascending/descending sorts

### Key Entities

- **Task**: Standard task entity with sortable fields (created_at, priority, due_date, title, completed)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sort applies within 200ms of selection
- **SC-002**: 100% accuracy in sort order (no misplaced tasks)
- **SC-003**: Sort persists across page refreshes and sessions
- **SC-004**: Sort works seamlessly with 100+ tasks without lag
- **SC-005**: Users can quickly understand and change sort order (95% success on first attempt)
- **SC-006**: Secondary sort (by created date) maintains stable ordering for equal values

## Assumptions *(mandatory)*

1. **Default Sort**: "Newest First" by created date on first visit
2. **Sort UI**: Dropdown above task list showing current sort option
3. **Sort + Filter**: Sort applies to filtered results (both work together)
4. **Client-side Sorting**: Sort on client side for Phase 2 (no API sort endpoint required)
5. **Persistence**: Sort preference stored in localStorage and URL query params
6. **Secondary Sort**: When primary sort values are equal, always use created date descending as tiebreaker
7. **Null Handling**: Null values (no priority, no due date) always sorted to end of list
