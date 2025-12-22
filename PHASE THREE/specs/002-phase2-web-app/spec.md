# Feature Specification: Full-Stack Web Application (Phase 2)

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-10
**Status**: Draft
**Input**: User description: "Transform Phase 1 CLI todo app into a modern multi-user web application with Next.js frontend, FastAPI backend, SQLModel ORM, Neon PostgreSQL database, and Better Auth JWT authentication. Maintain all 10 features from Phase 1 (Basic, Intermediate, Advanced levels) in web interface."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration and Authentication (Priority: P1)

As a new user, I want to create an account and log in securely, so I can access my personal todo list from anywhere with my credentials.

**Why this priority**: Authentication is the foundation for a multi-user system. Without it, we cannot isolate user data or provide personalized experiences. This is the critical first step before any task management functionality can work.

**Independent Test**: Can be fully tested by navigating to the signup page, creating an account with email/password, then logging in and verifying JWT token is issued and stored. Delivers value by enabling secure access to the application.

**Acceptance Scenarios**:

1. **Given** I am a new user on the homepage, **When** I click "Sign Up" and enter valid email and password, **Then** my account is created and I am redirected to my task dashboard
2. **Given** I have an existing account, **When** I enter correct email and password on login page, **Then** I receive a JWT token and am logged into my dashboard
3. **Given** I am logged in, **When** I close the browser and return later, **Then** my session is still valid (JWT not expired) and I see my tasks
4. **Given** I enter incorrect password, **When** I attempt to log in, **Then** I see "Invalid credentials" error message
5. **Given** I try to sign up with an existing email, **When** I submit the form, **Then** I see "Email already registered" error message

---

### User Story 2 - View Personal Task Dashboard (Priority: P1)

As a logged-in user, I want to see my task list displayed in a clean web interface, so I can quickly understand what tasks I need to complete.

**Why this priority**: Viewing tasks is the core read operation. Users need to see their tasks immediately after login to understand their todo list. This is essential before any create/update/delete operations.

**Independent Test**: Can be tested by logging in with a user who has existing tasks, and verifying the dashboard displays all their tasks with correct details (title, status, priority, due dates). Delivers value by providing instant visibility into pending work.

**Acceptance Scenarios**:

1. **Given** I am logged in with 5 existing tasks, **When** I land on the dashboard, **Then** I see all 5 tasks displayed in a table/list format with title, status, and priority
2. **Given** I have tasks with different statuses (pending/completed), **When** I view the dashboard, **Then** I see visual distinction between completed and pending tasks (e.g., strikethrough, checkmark)
3. **Given** I have no tasks yet, **When** I view the dashboard, **Then** I see an empty state message like "No tasks yet. Create your first task!"
4. **Given** I am on the dashboard, **When** another user logs in on a different device, **Then** they only see their own tasks, not mine
5. **Given** I have 50 tasks, **When** I view the dashboard, **Then** the page loads and displays within 2 seconds

---

### User Story 3 - Create New Task via Web Form (Priority: P1)

As a logged-in user, I want to create a new task using a web form, so I can quickly add todos with title, description, priority, tags, and due dates.

**Why this priority**: Task creation is the primary write operation. Users need to add tasks to their list before they can manage them. This delivers immediate value by allowing users to capture their work items.

**Independent Test**: Can be tested by clicking "Add Task" button, filling in the form with various fields (title required, others optional), submitting, and verifying the task appears in the dashboard. Delivers value by enabling task capture.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard, **When** I click "Add Task" button and fill in title "Buy groceries", **Then** a new task is created and appears in my task list
2. **Given** I am creating a task, **When** I fill in title, description, priority "high", tags "shopping,urgent", and due date "2025-12-15", **Then** all fields are saved and displayed correctly
3. **Given** I submit the form with empty title, **When** I try to create the task, **Then** I see validation error "Title is required"
4. **Given** I am creating a task with multi-line description, **When** I submit the form, **Then** the entire description with line breaks is preserved
5. **Given** I create a task, **When** the API request succeeds, **Then** I see a success message "Task created successfully" and the form is cleared

---

### User Story 4 - Update Existing Task (Priority: P2)

As a logged-in user, I want to edit any field of an existing task, so I can keep my task information current and accurate.

**Why this priority**: Tasks change over time - priorities shift, details get clarified, due dates move. This enables users to maintain accurate task data without deleting and recreating tasks.

**Independent Test**: Can be tested by clicking edit icon on a task, modifying any field (title, description, priority, tags, due date), saving, and verifying changes persist. Delivers value by allowing task refinement.

**Acceptance Scenarios**:

1. **Given** I have a task "Buy groceries", **When** I click edit icon, change title to "Buy groceries and cook dinner", and save, **Then** the task title is updated in the dashboard
2. **Given** I am editing a task, **When** I change priority from "low" to "high", **Then** the priority is updated and visually reflected (e.g., color change)
3. **Given** I am editing a task, **When** I add tags "work,urgent", **Then** the tags are saved and displayed on the task
4. **Given** I am editing a task, **When** I change due date from "2025-12-10" to "2025-12-20", **Then** the new due date is saved and displayed
5. **Given** I try to update task title to empty string, **When** I submit, **Then** I see validation error "Title cannot be empty"

---

### User Story 5 - Mark Task as Complete/Incomplete (Priority: P2)

As a logged-in user, I want to toggle task completion status with a single click, so I can quickly mark tasks done without opening a full edit form.

**Why this priority**: Task completion is a frequent action. Users need fast, frictionless way to mark tasks done. This provides immediate satisfaction and progress tracking.

**Independent Test**: Can be tested by clicking checkbox/toggle next to a pending task, verifying it moves to completed state with visual indication, then clicking again to revert. Delivers value by enabling quick status updates.

**Acceptance Scenarios**:

1. **Given** I have a pending task "Buy groceries", **When** I click the checkbox next to it, **Then** the task is marked completed with strikethrough text
2. **Given** I have a completed task, **When** I click the checkbox again, **Then** the task is marked incomplete and strikethrough is removed
3. **Given** I complete a task, **When** I refresh the page, **Then** the task still shows as completed (persisted to database)
4. **Given** I have a recurring task set to "daily", **When** I mark it complete, **Then** a new instance is automatically created for tomorrow
5. **Given** I toggle task status, **When** the API request fails (network error), **Then** the UI shows error message and reverts the checkbox state

---

### User Story 6 - Delete Task with Confirmation (Priority: P2)

As a logged-in user, I want to permanently delete tasks I no longer need, with confirmation to prevent accidental deletion.

**Why this priority**: Users need to remove completed or obsolete tasks to keep their list manageable. Confirmation prevents costly mistakes. This enables list hygiene.

**Independent Test**: Can be tested by clicking delete icon on a task, confirming the deletion dialog, and verifying the task is removed from the dashboard and database. Delivers value by enabling list cleanup.

**Acceptance Scenarios**:

1. **Given** I have a task "Old project", **When** I click delete icon and confirm "Yes, delete", **Then** the task is permanently removed from my list
2. **Given** I click delete icon, **When** I click "Cancel" on confirmation dialog, **Then** the task is NOT deleted and remains in my list
3. **Given** I delete a task, **When** I refresh the page, **Then** the deleted task does not reappear (removed from database)
4. **Given** I try to delete a task that doesn't belong to me (hacking attempt), **When** the API validates ownership, **Then** I receive 403 Forbidden error
5. **Given** I delete the last task in my list, **When** deletion succeeds, **Then** I see empty state message "No tasks yet"

---

### User Story 7 - Filter Tasks by Status, Priority, and Tags (Priority: P2)

As a logged-in user, I want to filter my task list by completion status, priority level, or tags, so I can focus on specific subsets of tasks.

**Why this priority**: As task lists grow, users need to narrow focus. Filtering by status shows what's pending, by priority shows what's urgent, by tags shows related tasks. This enables efficient task management.

**Independent Test**: Can be tested by selecting filter options (e.g., "Show only pending", "Priority: high", "Tag: work") and verifying only matching tasks are displayed. Delivers value by reducing cognitive load.

**Acceptance Scenarios**:

1. **Given** I have 20 tasks (10 pending, 10 completed), **When** I select filter "Status: Pending", **Then** only the 10 pending tasks are displayed
2. **Given** I have tasks with different priorities, **When** I select filter "Priority: High", **Then** only high-priority tasks are displayed
3. **Given** I have tasks tagged "work", "home", "shopping", **When** I select filter "Tag: work", **Then** only tasks with "work" tag are displayed
4. **Given** I apply multiple filters (Status: Pending AND Priority: High), **When** filters are active, **Then** only tasks matching ALL filters are displayed
5. **Given** I have filters applied, **When** I click "Clear filters", **Then** all tasks are displayed again

---

### User Story 8 - Search Tasks by Keyword (Priority: P3)

As a logged-in user, I want to search my tasks by keyword in title or description, so I can quickly find specific tasks without scrolling.

**Why this priority**: Search is essential for large task lists. Users need to locate tasks by remembering partial title or content. This enables quick task retrieval.

**Independent Test**: Can be tested by typing keyword in search box (e.g., "grocery") and verifying all tasks with "grocery" in title or description are displayed. Delivers value by enabling fast task lookup.

**Acceptance Scenarios**:

1. **Given** I have tasks "Buy groceries", "Plan grocery budget", "Schedule meeting", **When** I search for "grocery", **Then** the first two tasks are displayed
2. **Given** I search for "meeting", **When** the search executes, **Then** all tasks with "meeting" in title OR description are displayed
3. **Given** I search for a keyword that matches no tasks, **When** search executes, **Then** I see "No tasks found matching 'keyword'"
4. **Given** I have search results displayed, **When** I clear the search box, **Then** all tasks are displayed again
5. **Given** I search for "GROCERY" (uppercase), **When** search executes, **Then** results are case-insensitive and show "Buy groceries"

---

### User Story 9 - Sort Tasks by Multiple Criteria (Priority: P3)

As a logged-in user, I want to sort my task list by due date, priority, creation date, or title, so I can organize tasks according to my current focus.

**Why this priority**: Different contexts require different task order. Due date for deadline-driven work, priority for importance-driven work, title for alphabetical browsing. This enables flexible task organization.

**Independent Test**: Can be tested by clicking sort dropdown, selecting sort criteria (e.g., "Due date ascending"), and verifying tasks are reordered correctly. Delivers value by enabling contextual organization.

**Acceptance Scenarios**:

1. **Given** I have tasks with various due dates, **When** I select sort "Due date (ascending)", **Then** tasks are ordered from earliest to latest due date
2. **Given** I have tasks with different priorities, **When** I select sort "Priority (high to low)", **Then** tasks are ordered: high, medium, low, none
3. **Given** I have tasks created at different times, **When** I select sort "Created date (newest first)", **Then** most recent tasks appear first
4. **Given** I have tasks with titles A-Z, **When** I select sort "Title (alphabetical)", **Then** tasks are ordered alphabetically
5. **Given** I have sort applied, **When** I apply a filter, **Then** the filtered results maintain the current sort order

---

### User Story 10 - Set Up Recurring Tasks (Priority: P3)

As a logged-in user, I want to create tasks that repeat on a schedule (daily, weekly, monthly), so I can automate repetitive todos without manual creation.

**Why this priority**: Many tasks repeat - daily standup, weekly reports, monthly reviews. Recurring tasks eliminate manual recreation and ensure nothing is forgotten. This enables automation of routine work.

**Independent Test**: Can be tested by creating a task with recurrence "daily", marking it complete, and verifying a new instance is automatically created for tomorrow with the same details. Delivers value by automating repetitive task management.

**Acceptance Scenarios**:

1. **Given** I create a task "Daily standup" with recurrence "daily", **When** I mark it complete today, **Then** a new instance is created for tomorrow at the same time
2. **Given** I create a task "Weekly team meeting" with recurrence "weekly on Monday", **When** I complete it, **Then** a new instance is created for next Monday
3. **Given** I create a task "Monthly report" with recurrence "monthly on day 1", **When** I complete it on Jan 1, **Then** a new instance is created for Feb 1
4. **Given** I have a recurring task, **When** I edit the original task's title, **Then** future instances inherit the updated title
5. **Given** I delete a recurring task, **When** deletion succeeds, **Then** future instances are NOT created (recurrence is stopped)

---

### User Story 11 - Set Due Dates and Times with Reminders (Priority: P3)

As a logged-in user, I want to assign due dates and times to tasks and receive reminders, so I never miss important deadlines.

**Why this priority**: Time-sensitive tasks require deadline tracking. Due dates provide time context, reminders ensure timely action. This enables deadline management and prevents missed commitments.

**Independent Test**: Can be tested by creating a task with due date "2025-12-15" and time "14:00", then verifying the task shows countdown/overdue indicators appropriately. Delivers value by enabling time-based task management.

**Acceptance Scenarios**:

1. **Given** I create a task with due date "2025-12-15", **When** I view the dashboard, **Then** the task shows "Due in 5 days" countdown
2. **Given** I have a task due today at 14:00, **When** current time is 13:00, **Then** the task shows "Due in 1 hour" with visual urgency indicator
3. **Given** I have a task that is overdue (past due date/time), **When** I view the dashboard, **Then** the task shows "Overdue by 2 days" in red/warning color
4. **Given** I create a task with due date "2025-12-20" and time "10:00", **When** I view task details, **Then** I see full date and time "Dec 20, 2025 at 10:00 AM"
5. **Given** I set a task due time without date, **When** I submit the form, **Then** I see validation error "Due time requires a due date"

---

### Edge Cases

- What happens when user tries to access another user's tasks by manipulating URL (e.g., changing user_id)?
- What happens when JWT token expires while user is editing a task?
- What happens when user has 1000+ tasks - does pagination/virtualization kick in?
- What happens when two browser tabs are open and user completes task in one tab - does other tab sync?
- What happens when user loses internet connection while creating/updating a task?
- How does system handle invalid date formats or dates in the past for due dates?
- What happens when user tries to create recurring task with invalid recurrence pattern?
- What happens when database connection fails during API request?
- How does system handle extremely long titles (500+ characters) or descriptions (10000+ characters)?
- What happens when user uploads special characters, emojis, or non-Latin scripts in task fields?
- What happens when multiple users try to update the same task simultaneously (optimistic locking)?
- What happens when user deletes a task that has recurring instances - are future instances deleted?

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & User Management:**
- **FR-001**: System MUST provide user registration with email and password
- **FR-002**: System MUST validate email format and password strength (min 8 characters)
- **FR-003**: System MUST prevent duplicate email registrations
- **FR-004**: System MUST issue JWT tokens upon successful login
- **FR-005**: System MUST include user_id claim in JWT token payload
- **FR-006**: System MUST verify JWT token signature on every API request
- **FR-007**: System MUST expire JWT tokens after 7 days
- **FR-008**: System MUST provide logout functionality that clears JWT token
- **FR-009**: System MUST hash passwords using industry-standard algorithms (bcrypt/argon2)
- **FR-010**: System MUST enforce user data isolation - users can only access their own tasks

**Task CRUD Operations (Basic Level):**
- **FR-011**: System MUST allow users to create tasks with title (required) and description (optional)
- **FR-012**: System MUST validate task title is not empty and ≤200 characters
- **FR-013**: System MUST validate task description is ≤1000 characters
- **FR-014**: System MUST assign auto-incrementing unique ID to each task
- **FR-015**: System MUST associate each task with the authenticated user's user_id
- **FR-016**: System MUST allow users to view all their tasks in a list/table format
- **FR-017**: System MUST allow users to update any field of their existing tasks
- **FR-018**: System MUST allow users to toggle task completion status (complete/incomplete)
- **FR-019**: System MUST allow users to delete their own tasks with confirmation
- **FR-020**: System MUST persist all task data to PostgreSQL database

**Priorities & Tags (Intermediate Level):**
- **FR-021**: System MUST allow users to assign priority to tasks (high/medium/low/none)
- **FR-022**: System MUST allow users to add comma-separated tags to tasks
- **FR-023**: System MUST display priority with visual distinction (colors/icons)
- **FR-024**: System MUST display tags as clickable chips/badges
- **FR-025**: System MUST allow filtering tasks by priority level
- **FR-026**: System MUST allow filtering tasks by tag (exact match)

**Search & Filter (Intermediate Level):**
- **FR-027**: System MUST provide keyword search across task title and description
- **FR-028**: System MUST perform case-insensitive search
- **FR-029**: System MUST allow filtering tasks by completion status (all/pending/completed)
- **FR-030**: System MUST allow combining multiple filters (AND logic)
- **FR-031**: System MUST provide "Clear filters" functionality

**Sort (Intermediate Level):**
- **FR-032**: System MUST allow sorting tasks by: id, title, priority, due_date, created_at
- **FR-033**: System MUST allow sort order: ascending or descending
- **FR-034**: System MUST maintain sort order when filters are applied
- **FR-035**: System MUST persist sort preference across page refreshes

**Recurring Tasks (Advanced Level):**
- **FR-036**: System MUST allow users to set recurrence pattern: daily, weekly, or monthly
- **FR-037**: System MUST allow users to specify recurrence day (for weekly: 1-7 Mon-Sun, monthly: 1-31)
- **FR-038**: System MUST automatically create new task instance when recurring task is marked complete
- **FR-039**: System MUST inherit all fields (title, description, priority, tags) in new recurring instance
- **FR-040**: System MUST calculate next due date based on recurrence pattern
- **FR-041**: System MUST allow users to stop recurrence by editing/deleting original task

**Due Dates & Reminders (Advanced Level):**
- **FR-042**: System MUST allow users to set due date (YYYY-MM-DD format)
- **FR-043**: System MUST allow users to set due time (HH:MM format)
- **FR-044**: System MUST validate due time requires due date
- **FR-045**: System MUST display countdown for upcoming due dates ("Due in 3 days")
- **FR-046**: System MUST display overdue indicator for past-due tasks ("Overdue by 2 days")
- **FR-047**: System MUST visually highlight urgent tasks (due within 24 hours)
- **FR-048**: System MUST allow filtering by due date range

**API & Security:**
- **FR-049**: System MUST implement RESTful API with endpoints: GET/POST/PUT/DELETE/PATCH
- **FR-050**: System MUST return appropriate HTTP status codes (200/201/400/401/403/404/422/500)
- **FR-051**: System MUST validate all inputs with Pydantic models
- **FR-052**: System MUST return structured error responses with detail field
- **FR-053**: System MUST use parameterized queries to prevent SQL injection
- **FR-054**: System MUST escape user inputs in frontend to prevent XSS
- **FR-055**: System MUST enforce HTTPS in production
- **FR-056**: System MUST rate limit API requests to prevent abuse
- **FR-057**: System MUST log all authentication failures for security monitoring

**Database & Performance:**
- **FR-058**: System MUST create database indexes on user_id, completed, created_at, due_date
- **FR-059**: System MUST optimize queries to avoid N+1 problems
- **FR-060**: System MUST implement pagination for task lists (default 50 per page)
- **FR-061**: System MUST handle database connection failures gracefully
- **FR-062**: System MUST use connection pooling for database efficiency
- **FR-063**: System MUST automatically create database tables using SQLModel on first run

**Frontend & UX:**
- **FR-064**: System MUST provide responsive UI that works on desktop, tablet, and mobile
- **FR-065**: System MUST display loading states during API requests
- **FR-066**: System MUST display user-friendly error messages for all failures
- **FR-067**: System MUST provide visual feedback for all user actions (success/error toasts)
- **FR-068**: System MUST preserve form data on validation errors
- **FR-069**: System MUST implement keyboard shortcuts for common actions (Ctrl+N for new task)
- **FR-070**: System MUST provide accessibility features (ARIA labels, keyboard navigation)

### Key Entities

- **User**: Represents a registered user of the application
  - **Attributes (business view)**:
    - Unique identifier (UUID from Better Auth)
    - Email address (unique, used for login)
    - Full name (optional display name)
    - Password hash (never exposed to frontend)
    - Registration timestamp
    - Last login timestamp

- **Task**: Represents a todo item that users want to track and complete
  - **Attributes (business view)**:
    - Unique identifier (auto-increment integer)
    - User identifier (foreign key to User)
    - Title (required): Short, descriptive name of what needs to be done
    - Description (optional): Additional details, context, or instructions
    - Completion status: Boolean indicating done/not done
    - Priority level (optional): high, medium, low, or none
    - Tags (optional): Comma-separated labels for categorization
    - Due date (optional): Target date for completion
    - Due time (optional): Specific time for completion (requires due date)
    - Recurrence pattern (optional): daily, weekly, monthly, or none
    - Recurrence day (optional): Day of week (1-7) or month (1-31)
    - Creation timestamp: When the task was added
    - Last update timestamp: When the task was last modified

- **Session**: Represents an authenticated user session (managed by JWT)
  - **Attributes (business view)**:
    - JWT token (stored in browser localStorage/cookie)
    - User identifier (embedded in token as claim)
    - Expiration timestamp (7 days from issue)
    - Token signature (verified on every request)

### Assumptions

1. **Authentication Method**: Using Better Auth with JWT tokens (email/password flow, no OAuth for Phase 2)
2. **Database**: Neon Serverless PostgreSQL with automatic backups and scaling
3. **Token Storage**: JWT tokens stored in browser localStorage (httpOnly cookies in production)
4. **Password Policy**: Minimum 8 characters, no special character requirements for Phase 2
5. **Session Duration**: 7-day JWT expiration with no refresh tokens in Phase 2
6. **Concurrent Users**: System designed to handle 1,000 concurrent users
7. **Data Retention**: User data retained indefinitely unless user deletes account
8. **Character Encoding**: UTF-8 support for all text fields including unicode/emojis
9. **Time Zones**: All times stored in UTC, displayed in user's local timezone
10. **API Rate Limiting**: 100 requests per minute per user
11. **File Uploads**: Not supported in Phase 2 (text-only tasks)
12. **Real-time Sync**: Not implemented in Phase 2 (manual refresh required)
13. **Task Sharing**: Not supported in Phase 2 (single-user tasks only)
14. **Task History**: Not tracked in Phase 2 (no audit log of changes)
15. **Notification Delivery**: Due date reminders shown in-app only (no email/push notifications in Phase 2)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Authentication & User Management:**
- **SC-001**: Users can create account and log in within 30 seconds
- **SC-002**: 100% of JWT tokens are verified on every API request with 401 Unauthorized for invalid tokens
- **SC-003**: Users cannot access other users' tasks (100% data isolation)
- **SC-004**: Login success rate >95% for valid credentials
- **SC-005**: Password strength validation catches 100% of weak passwords (<8 characters)

**Task Management (Basic Level):**
- **SC-006**: Users can create a new task in under 10 seconds from clicking "Add Task" to seeing it in list
- **SC-007**: 100% of tasks with valid data are successfully stored in database and retrievable
- **SC-008**: Users can update any task field and see changes persist immediately
- **SC-009**: Task completion toggle responds within 500ms
- **SC-010**: Task deletion with confirmation prevents 100% of accidental deletions

**Priorities & Tags (Intermediate Level):**
- **SC-011**: Users can assign priority and see visual distinction (color/icon) immediately
- **SC-012**: Users can add multiple tags and see them as clickable chips
- **SC-013**: Priority filtering works correctly for all priority levels
- **SC-014**: Tag filtering shows only tasks with exact tag match

**Search & Filter (Intermediate Level):**
- **SC-015**: Search returns results within 500ms for lists up to 1,000 tasks
- **SC-016**: Search is case-insensitive and matches partial words correctly 100% of the time
- **SC-017**: Multiple filters (status + priority + tag) work together with AND logic
- **SC-018**: "Clear filters" restores full task list instantly

**Sort (Intermediate Level):**
- **SC-019**: Tasks sort correctly by any field (id, title, priority, due_date, created_at)
- **SC-020**: Sort order persists across page refreshes
- **SC-021**: Sorting 1,000 tasks completes within 1 second

**Recurring Tasks (Advanced Level):**
- **SC-022**: Marking recurring task complete automatically creates new instance within 1 second
- **SC-023**: New recurring instance inherits all fields (title, description, priority, tags) correctly
- **SC-024**: Next due date calculation is accurate for daily, weekly, and monthly patterns
- **SC-025**: Deleting recurring task stops future instance creation

**Due Dates & Reminders (Advanced Level):**
- **SC-026**: Tasks display accurate countdown for upcoming due dates ("Due in 3 days")
- **SC-027**: Overdue tasks show clear visual indicator (red text, warning icon)
- **SC-028**: Tasks due within 24 hours are highlighted prominently
- **SC-029**: Due date filtering shows tasks within specified date range correctly

**Performance & Reliability:**
- **SC-030**: Dashboard with 100 tasks loads within 2 seconds
- **SC-031**: System handles 1,000 concurrent users without degradation
- **SC-032**: API response time <500ms for 95th percentile requests
- **SC-033**: Database queries use indexes and avoid N+1 problems (verified by query analysis)
- **SC-034**: System uptime >99.5% (excluding planned maintenance)

**Security:**
- **SC-035**: 100% of API endpoints require valid JWT token (no unauthenticated access to tasks)
- **SC-036**: SQL injection attacks are prevented by parameterized queries
- **SC-037**: XSS attacks are prevented by proper input escaping in frontend
- **SC-038**: Rate limiting blocks >100 requests/minute per user

**User Experience:**
- **SC-039**: 95% of users successfully create their first task without documentation
- **SC-040**: Error messages are user-friendly and actionable (no technical jargon)
- **SC-041**: UI is responsive and works correctly on mobile devices (>375px width)
- **SC-042**: Loading states are displayed during all async operations
- **SC-043**: Success/error feedback is shown within 300ms of user action

**Code Quality:**
- **SC-044**: Backend test coverage >90% (pytest with pytest-cov)
- **SC-045**: Frontend test coverage >80% (Jest with React Testing Library)
- **SC-046**: Zero mypy type errors in strict mode
- **SC-047**: Zero TypeScript compiler errors
- **SC-048**: All linting passes (ruff for Python, ESLint for TypeScript)
- **SC-049**: Production build succeeds for both frontend and backend
- **SC-050**: All automated quality gates pass before deployment
