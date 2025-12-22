# Feature Specification: Mark Task Complete

**Feature Branch**: `004-mark-complete`
**Created**: 2025-12-06
**Status**: Approved
**Input**: User description: "Mark Complete - Toggle task completion status via CLI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mark Task as Complete (Priority: P1)

As a user, I want to mark a task as complete when I finish it, so I can track my progress and distinguish between pending and finished work.

**Why this priority**: Completing tasks is the core purpose of a todo app. Users need to mark tasks done to track accomplishments, reduce visual clutter of pending tasks, and maintain motivation through visible progress.

**Independent Test**: Can be fully tested by creating an incomplete task, marking it complete, then verifying the status changed and the task displays as completed in the task list.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 3, **When** I mark it as complete, **Then** task 3's status changes to complete and displays with completion indicator
2. **Given** I have marked a task as complete, **When** I view the task list, **Then** the completed task is visually distinct from incomplete tasks
3. **Given** I mark a task as complete, **When** I check the task details, **Then** the title, description, and ID remain unchanged

---

### User Story 2 - Unmark Task (Toggle to Incomplete) (Priority: P2)

As a user, I want to mark a completed task as incomplete again, so I can handle cases where I marked something done by mistake or need to redo a task.

**Why this priority**: Mistakes happen - users might accidentally mark the wrong task complete, or realize a "completed" task needs more work. The ability to toggle back provides flexibility and error correction.

**Independent Test**: Can be tested by marking a task complete, then unmarking it, and verifying the status toggles back to incomplete.

**Acceptance Scenarios**:

1. **Given** I have a completed task with ID 5, **When** I toggle its status, **Then** task 5 becomes incomplete again
2. **Given** I toggle a task's completion status multiple times, **When** I view the task, **Then** it reflects the current status accurately
3. **Given** I unmark a completed task, **When** I view the task list, **Then** it appears with incomplete tasks and incomplete status indicator

---

### Edge Cases

- What happens when trying to mark a non-existent task (invalid ID)?
- What happens when marking an already-complete task as complete (idempotent)?
- What happens when unmarking an already-incomplete task (idempotent)?
- How does the system handle rapid toggling of the same task?
- Does marking complete affect task order in the list?
- Can deleted tasks be marked complete (should fail)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to mark a task as complete by providing its ID
- **FR-002**: System MUST validate that the task ID exists before changing status
- **FR-003**: System MUST toggle task status (incomplete → complete, complete → incomplete)
- **FR-004**: System MUST preserve task ID, title, and description when changing status
- **FR-005**: System MUST provide clear visual distinction between complete and incomplete tasks in list view
- **FR-006**: System MUST provide confirmation when status change succeeds
- **FR-007**: System MUST display error message when task ID does not exist
- **FR-008**: System MUST support idempotent operations (marking complete task as complete has no effect but doesn't error)
- **FR-009**: System MUST update task status immediately (visible in next view command)
- **FR-010**: System MUST allow toggling status multiple times without side effects

### Key Entities

- **Task**: The todo item whose completion status is being changed
  - **Attribute being modified**:
    - Completion Status: Boolean or enum (incomplete/complete)
  - **Attributes unchanged**:
    - ID: Immutable identifier
    - Title: Not affected by status change
    - Description: Not affected by status change
    - Creation timestamp: Immutable

### Assumptions

1. **Toggle Behavior**: Single command toggles status (complete ↔ incomplete)
2. **Status Representation**: Use boolean or simple enum (two states only)
3. **Visual Indicators**: Text-based indicators in CLI (e.g., "[✓]" complete, "[ ]" incomplete)
4. **Default State**: New tasks created as incomplete
5. **Idempotency**: Marking complete task as complete succeeds without error (no-op)
6. **Immediate Effect**: Status change visible immediately in task list
7. **No Cascade**: Marking a task complete does not affect other tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Status changes complete in under 1 second from command to confirmation
- **SC-002**: 100% of status changes with valid task IDs succeed
- **SC-003**: 100% of status changes with invalid task IDs display appropriate errors
- **SC-004**: Completed tasks are visually distinct from incomplete tasks 100% of the time
- **SC-005**: Task ID, title, and description remain unchanged after 100% of status changes
- **SC-006**: Status changes are immediately visible in task list view
- **SC-007**: Users can toggle task status multiple times without errors
- **SC-008**: 98% of users understand how to mark tasks complete on first use
- **SC-009**: 100% of idempotent operations (marking complete task as complete) succeed without errors
