# Feature Specification: Priorities & Tags

**Feature Branch**: `006-priorities-tags`
**Created**: 2025-12-06
**Status**: Approved
**Input**: User description: "Priorities & Tags/Categories - Assign levels (high/medium/low) or labels (work/home) via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assign Priority Levels (Priority: P1)

As a user, I want to assign priority levels (high, medium, low) to tasks, so I can focus on what's most important and manage my time effectively.

**Why this priority**: Not all tasks are equally important. Priority levels help users identify critical tasks, make better decisions about what to work on first, and reduce overwhelm by clarifying importance.

**Independent Test**: Can be tested by creating tasks with different priority levels, then viewing the list to verify priorities are displayed and distinguishable.

**Acceptance Scenarios**:

1. **Given** I create a task, **When** I assign it high priority, **Then** the task is marked as high priority and displays accordingly
2. **Given** I have tasks with different priorities (high, medium, low), **When** I view the task list, **Then** priorities are clearly indicated for each task
3. **Given** I have a task with no priority assigned, **When** I view it, **Then** it shows default priority (medium or none)

---

### User Story 2 - Assign Tags/Categories (Priority: P1)

As a user, I want to assign tags or categories (work, home, personal, urgent) to tasks, so I can organize tasks by context and filter them by category.

**Why this priority**: Tasks belong to different life areas. Tags enable context-based organization (work tasks vs home tasks), making it easier to focus on relevant tasks based on current context (e.g., only show work tasks during work hours).

**Independent Test**: Can be tested by creating tasks with various tags, then viewing tasks to verify tags are displayed correctly.

**Acceptance Scenarios**:

1. **Given** I create a task, **When** I assign it the tag "work", **Then** the task is tagged as "work" and displays this tag
2. **Given** I have a task, **When** I assign multiple tags like "work" and "urgent", **Then** all tags are stored and displayed
3. **Given** I have tasks with different tags (work, home, personal), **When** I view the list, **Then** tags are clearly indicated for each task

---

### User Story 3 - Update Priority and Tags (Priority: P2)

As a user, I want to change a task's priority or tags after creation, so I can adapt to changing circumstances and reprioritize as needed.

**Why this priority**: Task importance changes over time. A low-priority task might become urgent, or a work task might shift to personal. The ability to update priorities and tags maintains system flexibility.

**Independent Test**: Can be tested by creating a task with initial priority/tags, updating them, then verifying the changes are reflected.

**Acceptance Scenarios**:

1. **Given** I have a low-priority task, **When** I change it to high priority, **Then** the priority updates and displays correctly
2. **Given** I have a task tagged "personal", **When** I change the tag to "work", **Then** the tag updates correctly
3. **Given** I have a task with multiple tags, **When** I add or remove tags, **Then** the tag list updates accordingly

---

### Edge Cases

- What happens when assigning an invalid priority level (e.g., "critical", "super-high")?
- What happens when assigning tags with special characters or very long names?
- What happens to tasks with no priority assigned (default behavior)?
- What happens to tasks with no tags (null/empty state)?
- Can a task have multiple tags simultaneously?
- How many tags can a single task have (limit)?
- What happens when filtering by a tag that no tasks have?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support three priority levels: high, medium, low
- **FR-002**: System MUST allow assigning priority when creating a task
- **FR-003**: System MUST allow changing priority of existing tasks
- **FR-004**: System MUST display priority level for each task in list view
- **FR-005**: System MUST support user-defined tags (strings like "work", "home", "urgent")
- **FR-006**: System MUST allow assigning one or more tags when creating a task
- **FR-007**: System MUST allow adding or removing tags from existing tasks
- **FR-008**: System MUST display tags for each task in list view
- **FR-009**: System MUST validate priority values (only high/medium/low accepted)
- **FR-010**: System MUST support tasks with no priority (default to medium or unset state)
- **FR-011**: System MUST support tasks with no tags (empty tag list)
- **FR-012**: System MUST allow multiple tags per task (minimum 1, maximum 10)
- **FR-013**: System MUST prevent duplicate tags on the same task
- **FR-014**: System MUST preserve priority and tags when updating other task attributes

### Key Entities

- **Task**: Enhanced with priority and tags
  - **New Attributes**:
    - Priority: Enum (high, medium, low) or nullable
    - Tags: List of strings (0-10 tags per task)
  - **Existing Attributes** (unchanged):
    - ID, title, description, completion status, creation timestamp

- **Priority Levels**:
  - High: Most important, needs immediate attention
  - Medium: Normal importance (default)
  - Low: Can be deferred, low urgency

- **Tags**:
  - Free-form text labels (e.g., "work", "home", "urgent", "project-x")
  - Case-insensitive (e.g., "Work" and "work" treated as same tag)
  - Maximum length: 50 characters per tag

### Assumptions

1. **Default Priority**: Tasks without explicit priority default to "medium" or show as "unset"
2. **Default Tags**: Tasks without tags have empty tag list (not an error)
3. **Tag Format**: Alphanumeric strings, hyphens, underscores allowed; no spaces within a tag
4. **Tag Limits**: Maximum 10 tags per task to prevent abuse
5. **Priority Display**: Visual indicators (e.g., "!" for high, "-" for low) or color coding (if terminal supports)
6. **Tag Display**: Comma-separated list or tag chips in list view
7. **Case Sensitivity**: Tags are case-insensitive ("Work" = "work")

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priority to a task in under 3 seconds
- **SC-002**: Users can assign tags to a task in under 5 seconds
- **SC-003**: 100% of tasks display their priority correctly in list view
- **SC-004**: 100% of tasks display their tags correctly in list view
- **SC-005**: Priority and tag updates are immediately visible in task list
- **SC-006**: Invalid priority values are rejected 100% of the time with clear error messages
- **SC-007**: Users can assign up to 10 tags per task without errors
- **SC-008**: Duplicate tags on same task are prevented 100% of the time
- **SC-009**: 90% of users understand priority levels without documentation
- **SC-010**: Tasks with priorities and tags can be filtered and sorted correctly
