# Feature Specification: Sort Tasks

**Feature Branch**: `008-sort-tasks`
**Created**: 2025-12-06
**Status**: Approved
**Input**: User description: "Sort Tasks - Reorder by due date, priority, or alphabetically via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sort by Priority (Priority: P1)

As a user, I want to sort tasks by priority (high to low), so I can see the most important tasks first and plan my work accordingly.

**Why this priority**: Sorting by priority aligns task list order with importance, enabling users to work on high-priority items first without manually searching for them.

**Independent Test**: Can be tested by creating tasks with different priorities, sorting by priority, then verifying tasks appear in correct order (high, medium, low).

**Acceptance Scenarios**:

1. **Given** I have tasks with mixed priorities, **When** I sort by priority descending, **Then** high-priority tasks appear first, followed by medium, then low
2. **Given** I have tasks sorted by priority, **When** I view the list, **Then** the order is: high → medium → low
3. **Given** multiple tasks have the same priority, **When** sorted by priority, **Then** tasks with same priority maintain their relative order (stable sort)

---

### User Story 2 - Sort by Due Date (Priority: P1)

As a user, I want to sort tasks by due date (earliest first), so I can focus on approaching deadlines and avoid missing due dates.

**Why this priority**: Due date sorting helps users identify urgent tasks and manage time-sensitive work effectively, preventing missed deadlines.

**Independent Test**: Can be tested by creating tasks with different due dates, sorting by due date, then verifying tasks appear in chronological order.

**Acceptance Scenarios**:

1. **Given** I have tasks with due dates, **When** I sort by due date ascending, **Then** tasks with earliest due dates appear first
2. **Given** some tasks have no due date, **When** I sort by due date, **Then** tasks with no due date appear at the end
3. **Given** multiple tasks have the same due date, **When** sorted by due date, **Then** they maintain relative order

---

### User Story 3 - Sort Alphabetically by Title (Priority: P2)

As a user, I want to sort tasks alphabetically by title, so I can quickly locate tasks by name in large lists.

**Why this priority**: Alphabetical sorting provides predictable, familiar ordering that helps users find tasks by name, especially useful for large lists.

**Independent Test**: Can be tested by creating tasks with various titles, sorting alphabetically, then verifying correct A-Z order.

**Acceptance Scenarios**:

1. **Given** I have tasks with titles "Zebra", "Apple", "Mango", **When** I sort alphabetically ascending, **Then** the order is: Apple, Mango, Zebra
2. **Given** I sort alphabetically, **When** titles start with lowercase or uppercase letters, **Then** sorting is case-insensitive
3. **Given** I sort alphabetically descending (Z-A), **When** I view the list, **Then** tasks appear in reverse alphabetical order

---

### User Story 4 - Default Sort Order (Priority: P3)

As a user, I want to reset to default sort order (by creation date/ID), so I can return to the original chronological view.

**Why this priority**: Default ordering provides consistency. After experimenting with different sort orders, users may want to return to the familiar chronological view.

**Independent Test**: Can be tested by applying custom sort, then resetting to default, and verifying tasks appear in ID/creation order.

**Acceptance Scenarios**:

1. **Given** I have sorted tasks by priority, **When** I reset to default order, **Then** tasks appear in creation order (by ID)
2. **Given** I apply default sorting, **When** I create a new task, **Then** it appears at the end of the list (newest)

---

### Edge Cases

- What happens when sorting by due date when no tasks have due dates?
- What happens when sorting by priority when all tasks have the same priority?
- What happens when sorting an empty list (no tasks)?
- How does sorting handle tasks with null/unset values (e.g., no priority)?
- Does sorting affect filtered views (e.g., sort only filtered tasks)?
- Can sorting be combined with search/filter?
- How does reverse/descending sort work for each criterion?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support sorting by priority (high to low, low to high)
- **FR-002**: System MUST support sorting by due date (earliest to latest, latest to earliest)
- **FR-003**: System MUST support sorting alphabetically by title (A-Z, Z-A)
- **FR-004**: System MUST support default sort order (by creation date/ID)
- **FR-005**: System MUST maintain stable sort (preserve relative order for equal values)
- **FR-006**: System MUST handle tasks with null/unset sort values (place at end or use defaults)
- **FR-007**: System MUST support ascending and descending sort for all criteria
- **FR-008**: System MUST apply sort to filtered views (sort only visible tasks)
- **FR-009**: System MUST display sorted results immediately after sort command
- **FR-010**: System MUST indicate current sort order in view (e.g., "Sorted by: Priority (High to Low)")

### Key Entities

- **Task**: Entity being sorted
  - **Sortable Attributes**:
    - Priority: Enum (high > medium > low)
    - Due Date: DateTime (earlier < later)
    - Title: String (alphabetical A-Z)
    - Creation Date/ID: Integer (lower ID = created earlier)

- **Sort Criteria**:
  - Priority: high/medium/low ordering
  - Due Date: chronological ordering
  - Title: lexicographic ordering (case-insensitive)
  - Default: ID/creation order

### Assumptions

1. **Default Order**: Tasks sorted by ID (creation order) when no sort applied
2. **Null Handling**: Tasks with no due date appear at end when sorting by due date; tasks with no priority use default "medium" for sorting
3. **Case Insensitivity**: Alphabetical sort is case-insensitive ("Apple" before "banana")
4. **Stable Sort**: Equal values maintain original relative order
5. **Sort Persistence**: Sort order resets after view (not saved between commands)
6. **Performance**: Sorting completes in under 1 second for 1000 tasks
7. **Combined with Filters**: Sort applies to filtered results, not full list

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sorting completes in under 1 second for lists up to 1000 tasks
- **SC-002**: Priority sort displays tasks in correct order 100% of the time
- **SC-003**: Due date sort displays tasks in chronological order 100% of the time
- **SC-004**: Alphabetical sort displays tasks in A-Z order 100% of the time
- **SC-005**: Stable sort preserves relative order for equal values 100% of the time
- **SC-006**: Tasks with null values (no due date, no priority) are handled correctly without errors
- **SC-007**: Ascending and descending sorts work correctly for all criteria
- **SC-008**: Sort applies correctly to filtered views (sorts only filtered tasks)
- **SC-009**: 95% of users successfully sort tasks by priority on first attempt
- **SC-010**: Current sort order is clearly indicated in task list view
