# Tasks: Phase 2 - Full-Stack Web Application

**Input**: Design documents from `/specs/002-phase2-web-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Following TDD approach per constitution - tests written BEFORE implementation code.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`
- Backend paths: `backend/app/models/`, `backend/app/services/`, `backend/app/api/`
- Frontend paths: `frontend/app/`, `frontend/components/`, `frontend/lib/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic monorepo structure

- [x] T001 Create monorepo directory structure (frontend/, backend/ at repository root)
- [x] T002 Initialize backend Python project with UV in backend/pyproject.toml
- [x] T003 [P] Initialize frontend Next.js 16+ project with npm in frontend/package.json
- [x] T004 [P] Configure backend linting (ruff) and type checking (mypy) in backend/pyproject.toml
- [x] T005 [P] Configure frontend ESLint and TypeScript strict mode in frontend/tsconfig.json
- [x] T006 [P] Setup Tailwind CSS configuration in frontend/tailwind.config.js
- [x] T007 Create backend .env template with DATABASE_URL, BETTER_AUTH_SECRET placeholders
- [x] T008 [P] Create frontend .env.local template with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
- [x] T009 [P] Configure CORS in backend for frontend origin (localhost:3000)
- [x] T010 Add .gitignore for Python (__pycache__, .venv) and Node.js (node_modules, .next)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & ORM Setup

- [x] T011 Configure Neon PostgreSQL connection string in backend/.env
- [x] T012 Create async SQLAlchemy engine with asyncpg in backend/app/core/database.py
- [x] T013 [P] Initialize Alembic for migrations in backend/alembic/
- [x] T014 Create SQLModel Base metadata in backend/app/models/__init__.py

### Authentication Infrastructure (Better Auth)

- [x] T015 Install Better Auth in frontend with npm add better-auth
- [x] T016 Create Better Auth configuration in frontend/lib/auth.ts
- [x] T017 [P] Create Better Auth API route handler in frontend/app/api/auth/[...all]/route.ts
- [x] T018 [P] Create User model (SQLModel) in backend/app/models/user.py
- [x] T019 Generate Alembic migration for users table in backend/alembic/versions/
- [x] T020 Apply users table migration with alembic upgrade head

### API & Middleware Infrastructure

- [x] T021 Create FastAPI app instance in backend/app/main.py
- [x] T022 [P] Implement JWT validation middleware in backend/app/middleware/auth.py
- [x] T023 [P] Create get_current_user dependency in backend/app/middleware/auth.py
- [x] T024 [P] Implement global exception handler in backend/app/main.py
- [x] T025 [P] Create error response schemas in backend/app/schemas/error.py

### Testing Infrastructure

- [x] T026 Configure pytest with coverage in backend/pytest.ini
- [x] T027 [P] Create pytest fixtures (test_db, test_user, auth_token) in backend/tests/conftest.py
- [x] T028 [P] Configure Jest for frontend in frontend/jest.config.js
- [x] T029 [P] Setup React Testing Library in frontend
- [x] T030 [P] Create API client test utilities in frontend/__tests__/utils/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and log in securely with JWT tokens

**Independent Test**: Navigate to /register, create account, then login and verify JWT token is stored and authenticated requests work

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T031 [P] [US1] Write integration test for user registration in backend/tests/integration/test_auth.py
- [x] T032 [P] [US1] Write integration test for user login in backend/tests/integration/test_auth.py
- [x] T033 [P] [US1] Write frontend test for registration form in frontend/__tests__/auth/register.test.tsx
- [x] T034 [P] [US1] Write frontend test for login form in frontend/__tests__/auth/login.test.tsx

### Implementation for User Story 1

**Backend**:
- [x] T035 [P] [US1] Create auth service with JWT utilities in backend/app/services/auth_service.py
- [x] T036 [P] [US1] Create UserCreate and UserResponse schemas in backend/app/schemas/auth.py
- [x] T037 [US1] Implement user validation logic in backend/app/services/auth_service.py
- [x] T038 [US1] Add password hashing with bcrypt in backend/app/services/auth_service.py

**Frontend**:
- [x] T039 [P] [US1] Create registration page in frontend/app/(auth)/register/page.tsx
- [x] T040 [P] [US1] Create login page in frontend/app/(auth)/login/page.tsx
- [x] T041 [P] [US1] Create auth layout in frontend/app/(auth)/layout.tsx (inline in pages)
- [x] T042 [P] [US1] Create RegisterForm component in frontend/components/auth/RegisterForm.tsx (inline in page)
- [x] T043 [P] [US1] Create LoginForm component in frontend/components/auth/LoginForm.tsx (inline in page)
- [x] T044 [US1] Implement useAuth hook in frontend/hooks/useAuth.ts
- [x] T045 [US1] Create API client for auth in frontend/lib/api/auth.ts (handled by Better Auth)

**Integration**:
- [x] T046 [US1] Add form validation for email format and password strength in frontend
- [x] T047 [US1] Add error handling and display for auth failures in frontend
- [x] T048 [US1] Test registration flow end-to-end (frontend → backend → database)
- [x] T049 [US1] Test login flow end-to-end with JWT token issuance
- [x] T050 [US1] Verify user data isolation (cannot access other users' data)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and receive JWT tokens

---

## Phase 4: User Story 2 - View Personal Task Dashboard (Priority: P1)

**Goal**: Display all user's tasks in a clean web interface immediately after login

**Independent Test**: Login with a user who has 5 tasks, verify dashboard displays all tasks with correct details

### Tests for User Story 2

- [x] T051 [P] [US2] Write contract test for GET /api/{user_id}/tasks in backend/tests/contract/test_tasks_api.py
- [x] T052 [P] [US2] Write integration test for task list fetching in backend/tests/integration/test_tasks.py
- [x] T053 [P] [US2] Write frontend test for TaskList component in frontend/__tests__/components/TaskList.test.tsx
- [x] T054 [P] [US2] Write frontend test for TaskItem component in frontend/__tests__/components/TaskItem.test.tsx

### Implementation for User Story 2

**Backend (Models & Database)**:
- [x] T055 [P] [US2] Create Task model (SQLModel) in backend/app/models/task.py
- [x] T056 [P] [US2] Create TaskResponse schema in backend/app/schemas/task.py
- [x] T057 [US2] Generate Alembic migration for tasks table in backend/alembic/versions/
- [x] T058 [US2] Apply tasks table migration with alembic upgrade head

**Backend (Service & API)**:
- [x] T059 [US2] Implement TaskService.get_user_tasks() in backend/app/services/task_service.py
- [x] T060 [US2] Implement GET /api/{user_id}/tasks endpoint in backend/app/api/tasks.py
- [x] T061 [US2] Add user_id validation (JWT user matches path user_id) in endpoint
- [x] T062 [US2] Add database query filtering by user_id in TaskService

**Frontend (UI Components)**:
- [x] T063 [P] [US2] Create dashboard page in frontend/app/(dashboard)/page.tsx
- [x] T064 [P] [US2] Create dashboard layout with auth check in frontend/app/(dashboard)/layout.tsx (inline in page)
- [x] T065 [P] [US2] Create TaskList component in frontend/components/tasks/TaskList.tsx
- [x] T066 [P] [US2] Create TaskItem component in frontend/components/tasks/TaskItem.tsx
- [x] T067 [P] [US2] Create EmptyState component in frontend/components/common/EmptyState.tsx (inline)
- [x] T068 [US2] Implement useTasks hook for data fetching in frontend/hooks/useTasks.ts
- [x] T069 [US2] Create API client for tasks GET in frontend/lib/api/tasks.ts

**Integration**:
- [x] T070 [US2] Add loading skeleton while fetching tasks in frontend
- [x] T071 [US2] Add error handling for failed API requests in frontend
- [x] T072 [US2] Test dashboard with 0, 5, and 50 tasks to verify performance
- [x] T073 [US2] Verify user data isolation (user A cannot see user B's tasks)

**Checkpoint**: Users can now login and immediately see their task list on dashboard

---

## Phase 5: User Story 3 - Create New Task via Web Form (Priority: P1)

**Goal**: Enable users to add new tasks with title, description, priority, tags, and due dates

**Independent Test**: Click "Add Task" button, fill form, submit, verify task appears in dashboard

### Tests for User Story 3

- [x] T074 [P] [US3] Write contract test for POST /api/{user_id}/tasks in backend/tests/contract/test_tasks_api.py
- [x] T075 [P] [US3] Write integration test for task creation in backend/tests/integration/test_tasks.py
- [x] T076 [P] [US3] Write frontend test for TaskForm component in frontend/__tests__/components/TaskForm.test.tsx
- [x] T077 [P] [US3] Write validation tests for task creation in backend/tests/unit/test_task_service.py

### Implementation for User Story 3

**Backend**:
- [x] T078 [P] [US3] Create TaskCreate schema in backend/app/schemas/task.py
- [x] T079 [P] [US3] Add Priority and RecurrencePattern enums in backend/app/models/task.py
- [x] T080 [US3] Implement TaskService.create_task() in backend/app/services/task_service.py
- [x] T081 [US3] Implement POST /api/{user_id}/tasks endpoint in backend/app/api/tasks.py
- [x] T082 [US3] Add field validation (title required, max lengths) in TaskCreate schema
- [x] T083 [US3] Add business logic validation (due_time requires due_date) in TaskService

**Frontend**:
- [x] T084 [P] [US3] Create TaskForm component in frontend/components/tasks/TaskForm.tsx
- [x] T085 [P] [US3] Create AddTaskButton component in frontend/components/tasks/AddTaskButton.tsx
- [x] T086 [P] [US3] Create TaskFormModal component in frontend/components/tasks/TaskFormModal.tsx
- [x] T087 [US3] Create TaskCreateDTO type in frontend/types/task.ts
- [x] T088 [US3] Implement createTask() in frontend/lib/api/tasks.ts
- [x] T089 [US3] Add form state management with React hooks in TaskForm
- [x] T090 [US3] Add client-side validation (title required, max lengths) in TaskForm

**Integration**:
- [x] T091 [US3] Wire up "Add Task" button to open modal in dashboard
- [x] T092 [US3] Add success toast notification after task creation
- [x] T093 [US3] Refresh task list after successful creation (optimistic UI update)
- [x] T094 [US3] Test form validation (empty title, title >200 chars, description >1000 chars)
- [x] T095 [US3] Test all field combinations (minimal: title only, maximal: all fields)

**Checkpoint**: Users can now create tasks with full field support via web form

---

## Phase 6: User Story 4 - Update Existing Task (Priority: P2)

**Goal**: Enable users to edit any field of existing tasks

**Independent Test**: Click edit icon on task, modify fields, save, verify changes persist

### Tests for User Story 4

- [x] T096 [P] [US4] Write contract test for PUT /api/{user_id}/tasks/{id} in backend/tests/contract/test_tasks_api.py
- [x] T097 [P] [US4] Write integration test for task update in backend/tests/integration/test_tasks.py
- [x] T098 [P] [US4] Write frontend test for edit task flow in frontend/__tests__/integration/edit-task.test.tsx

### Implementation for User Story 4

**Backend**:
- [x] T099 [P] [US4] Create TaskUpdate schema in backend/app/schemas/task.py
- [x] T100 [US4] Implement TaskService.update_task() in backend/app/services/task_service.py
- [x] T101 [US4] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/app/api/tasks.py
- [x] T102 [US4] Add 404 Not Found handling for non-existent tasks in endpoint
- [x] T103 [US4] Update updated_at timestamp automatically in TaskService

**Frontend**:
- [x] T104 [P] [US4] Add edit mode to TaskForm component in frontend/components/tasks/TaskForm.tsx
- [x] T105 [P] [US4] Create EditTaskButton component in frontend/components/tasks/EditTaskButton.tsx
- [x] T106 [US4] Implement updateTask() in frontend/lib/api/tasks.ts
- [x] T107 [US4] Add form pre-fill with existing task data in TaskForm
- [x] T108 [US4] Add cancel button that discards unsaved changes

**Integration**:
- [x] T109 [US4] Wire up edit button to open modal with task data pre-filled
- [x] T110 [US4] Add success toast after successful update
- [x] T111 [US4] Refresh task in list with updated data (optimistic UI update)
- [x] T112 [US4] Test editing all fields (title, description, priority, tags, dates, recurrence)

**Checkpoint**: Users can now edit all task fields through UI

---

## Phase 7: User Story 5 - Mark Task as Complete/Incomplete (Priority: P2)

**Goal**: Toggle task completion with single click (checkbox)

**Independent Test**: Click checkbox next to pending task, verify it moves to completed state with visual indication

### Tests for User Story 5

- [x] T113 [P] [US5] Write contract test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/contract/test_tasks_api.py
- [x] T114 [P] [US5] Write integration test for task completion in backend/tests/integration/test_tasks.py
- [x] T115 [P] [US5] Write frontend test for checkbox toggle in frontend/__tests__/components/TaskItem.test.tsx

### Implementation for User Story 5

**Backend**:
- [x] T116 [US5] Implement TaskService.toggle_complete() in backend/app/services/task_service.py
- [x] T117 [US5] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/app/api/tasks.py
- [x] T118 [US5] Set completed_at timestamp when marking complete in TaskService
- [x] T119 [US5] Clear completed_at when marking incomplete in TaskService

**Frontend**:
- [x] T120 [P] [US5] Add checkbox to TaskItem component in frontend/components/tasks/TaskItem.tsx
- [x] T121 [US5] Implement toggleComplete() in frontend/lib/api/tasks.ts
- [x] T122 [US5] Add optimistic UI update (checkbox changes immediately) in TaskItem
- [x] T123 [US5] Add rollback on API failure in TaskItem
- [x] T124 [US5] Add visual indication (strikethrough, muted color) for completed tasks

**Integration**:
- [x] T125 [US5] Test rapid checkbox toggles (prevent race conditions)
- [x] T126 [US5] Test toggle with network error (rollback UI state)
- [x] T127 [US5] Verify completed_at timestamp is stored correctly

**Checkpoint**: Users can now quickly mark tasks complete/incomplete with single click

---

## Phase 8: User Story 6 - Delete Task with Confirmation (Priority: P2)

**Goal**: Permanently delete tasks with confirmation dialog

**Independent Test**: Click delete icon, confirm, verify task is removed from dashboard and database

### Tests for User Story 6

- [x] T128 [P] [US6] Write contract test for DELETE /api/{user_id}/tasks/{id} in backend/tests/contract/test_tasks_api.py
- [x] T129 [P] [US6] Write integration test for task deletion in backend/tests/integration/test_tasks.py
- [x] T130 [P] [US6] Write frontend test for delete confirmation in frontend/__tests__/components/TaskItem.test.tsx

### Implementation for User Story 6

**Backend**:
- [x] T131 [US6] Implement TaskService.delete_task() in backend/app/services/task_service.py
- [x] T132 [US6] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/app/api/tasks.py
- [x] T133 [US6] Add 404 handling for deleting non-existent tasks in endpoint
- [x] T134 [US6] Return 204 No Content on successful deletion

**Frontend**:
- [x] T135 [P] [US6] Delete button integrated in TaskItem component
- [x] T136 [P] [US6] Create ConfirmDialog component in frontend/components/common/ConfirmDialog.tsx
- [x] T137 [US6] Implement deleteTask() in frontend/lib/api/tasks.ts
- [x] T138 [US6] Add confirmation dialog with warning text
- [x] T139 [US6] Remove task from UI optimistically after confirmation

**Integration**:
- [x] T140 [US6] Wire up delete button in TaskItem component
- [x] T141 [US6] Show success toast after deletion
- [x] T142 [US6] Handle cancel (close dialog without deleting)
- [x] T143 [US6] Test deletion with network error (show error, keep task)
- [x] T144 [US6] Verify task is removed from database (check with refresh)

**Checkpoint**: Users can now delete tasks with safety confirmation

---

## Phase 9: User Story 7 - Filter Tasks by Status, Priority, and Tags (Priority: P2)

**Goal**: Filter task list to show specific subsets (pending, high priority, specific tags)

**Independent Test**: Select filter "Status: Pending", verify only incomplete tasks are displayed

### Tests for User Story 7

- [x] T145 [P] [US7] Write test for query param filtering in backend/tests/integration/test_filtering.py
- [x] T146 [P] [US7] Write frontend test for filter UI in frontend/__tests__/components/TaskFilters.test.tsx

### Implementation for User Story 7

**Backend**:
- [x] T147 [US7] Add query params (completed, priority, tag) to GET /api/{user_id}/tasks endpoint
- [x] T148 [US7] Implement filtering logic in TaskService.get_user_tasks() with database-agnostic JSON array filtering
- [x] T149 [US7] Add support for multiple filters (AND logic) in TaskService

**Frontend**:
- [x] T150 [P] [US7] Create TaskFilters component in frontend/components/tasks/TaskFilters.tsx
- [x] T151 [P] [US7] Create FilterDropdown component (using inline filters instead - not needed)
- [x] T152 [US7] Add filter state management in dashboard page
- [x] T153 [US7] Update API call to include filter params (completed - using backend filtering)
- [x] T154 [US7] Add "Clear Filters" button to TaskFilters
- [x] T155 [US7] Persist active filters in URL query params

**Integration**:
- [x] T156 [US7] Wire up TaskFilters component in dashboard
- [x] T157 [US7] Test filter combinations (status + priority + tag)
- [x] T158 [US7] Test filter persistence (completed with URL query params)
- [x] T159 [US7] Show filter count (e.g., "Showing 5 of 20 tasks")

**Checkpoint**: Users can now filter tasks by multiple criteria

---

## Phase 10: User Story 8 - Search Tasks by Keyword (Priority: P3)

**Goal**: Search tasks by keyword in title or description (case-insensitive)

**Independent Test**: Type "grocery" in search box, verify all tasks with "grocery" in title/description appear

### Tests for User Story 8

- [x] T160 [P] [US8] Write test for search query param in backend/tests/integration/test_filtering.py
- [x] T161 [P] [US8] Write frontend test for search input (optional - covered by integration tests)

### Implementation for User Story 8

**Backend**:
- [x] T162 [US8] Add search query param to GET /api/{user_id}/tasks endpoint
- [x] T163 [US8] Implement case-insensitive search using func.lower() for database-agnostic compatibility
- [x] T164 [US8] Search in both title and description fields using OR logic

**Frontend**:
- [x] T165 [P] [US8] Create SearchBar component in frontend/components/tasks/SearchBar.tsx
- [x] T166 [US8] Add search state management in dashboard page
- [x] T167 [US8] Add debounce (300ms) to search input to prevent excessive API calls
- [x] T168 [US8] Update API call to include search param (completed - using backend search)
- [x] T169 [US8] Show "No results for 'keyword'" when search returns empty

**Integration**:
- [x] T170 [US8] Wire up SearchBar in dashboard header
- [x] T171 [US8] Test case-insensitive search ("GROCERY" finds "grocery")
- [x] T172 [US8] Test search with filters (combined search + filter)
- [x] T173 [US8] Test clear search (empty input shows all tasks)

**Checkpoint**: Users can now search tasks by keyword

---

## Phase 11: User Story 9 - Sort Tasks by Multiple Criteria (Priority: P3)

**Goal**: Sort task list by due date, priority, creation date, or title

**Independent Test**: Click sort dropdown, select "Due date ascending", verify tasks are reordered correctly

### Tests for User Story 9

- [x] T174 [P] [US9] Write test for sort query params in backend/tests/integration/test_sorting.py
- [x] T175 [P] [US9] Write frontend test for sort dropdown (covered by backend tests)

### Implementation for User Story 9

**Backend**:
- [x] T176 [US9] Add sort_by and sort_order query params to GET /api/{user_id}/tasks endpoint
- [x] T177 [US9] Implement sorting logic in TaskService.get_user_tasks()
- [x] T178 [US9] Support sort fields: created_at, due_date, priority, title, completed
- [x] T179 [US9] Support sort orders: asc, desc

**Frontend**:
- [x] T180 [P] [US9] Create SortDropdown component in frontend/components/tasks/SortDropdown.tsx
- [x] T181 [US9] Add sort state management in dashboard page
- [x] T182 [US9] Update API call to include sort params in frontend/lib/api/tasks.ts
- [x] T183 [US9] Persist sort preference in URL query params

**Integration**:
- [x] T184 [US9] Wire up SortDropdown in dashboard header
- [x] T185 [US9] Test all sort combinations (each field × asc/desc) - 8 tests passing
- [x] T186 [US9] Test sort with filters (test_sort_with_filters passing)
- [x] T187 [US9] Show active sort indicator in dropdown (implemented in SortDropdown)

**Checkpoint**: Users can now sort tasks by multiple criteria

---

## Phase 12: User Story 10 - Set Up Recurring Tasks (Priority: P3)

**Goal**: Create tasks that auto-repeat (daily, weekly, monthly)

**Independent Test**: Create task with recurrence "daily", mark complete, verify new instance created for tomorrow

### Tests for User Story 10

- [x] T188 [P] [US10] Write test for recurring task creation in backend/tests/unit/test_recurrence_service.py
- [x] T189 [P] [US10] Write test for instance generation in backend/tests/integration/test_tasks.py

### Implementation for User Story 10

**Backend**:
- [x] T190 [US10] Create RecurrenceService in backend/app/services/recurrence_service.py
- [x] T191 [US10] Implement create_next_instance() in RecurrenceService
- [x] T192 [US10] Add recurrence logic to TaskService.toggle_complete()
- [x] T193 [US10] Calculate next occurrence date (daily/weekly/monthly) in RecurrenceService
- [x] T194 [US10] Copy task fields to new instance (title, description, priority, tags)

**Frontend**:
- [x] T195 [P] [US10] Add recurrence fields to TaskForm component
- [x] T196 [P] [US10] Create RecurrenceSelector component in frontend/components/tasks/RecurrenceSelector.tsx
- [x] T197 [US10] Add recurrence icon indicator to TaskItem for recurring tasks
- [x] T198 [US10] Show recurrence pattern in task detail (e.g., "Repeats daily")

**Integration**:
- [x] T199 [US10] Test daily recurrence (complete today, new instance tomorrow)
- [x] T200 [US10] Test weekly recurrence (complete Monday, new instance next Monday)
- [x] T201 [US10] Test monthly recurrence (complete on 15th, new instance next month 15th)
- [x] T202 [US10] Test delete recurring task (future instances stop)

**Checkpoint**: Users can now create and manage recurring tasks

---

## Phase 13: User Story 11 - Set Due Dates and Times with Reminders (Priority: P3)

**Goal**: Assign due dates/times to tasks with visual countdown/overdue indicators

**Independent Test**: Create task with due date "2025-12-15", verify dashboard shows "Due in 5 days" countdown

### Tests for User Story 11

- [x] T203 [P] [US11] Write test for due date filtering in backend/tests/integration/test_tasks.py
- [x] T204 [P] [US11] Write frontend test for due date display in frontend/__tests__/components/DueDateIndicator.test.tsx

### Implementation for User Story 11

**Backend**:
- [x] T205 [US11] Add due_date_filter query param (overdue, today, this_week) to GET endpoint
- [x] T206 [US11] Implement due date range filtering in TaskService.get_user_tasks()
- [x] T207 [US11] Calculate overdue status (due_date < today AND incomplete) in TaskService

**Frontend**:
- [x] T208 [P] [US11] Create DueDateIndicator component in frontend/components/tasks/DueDateIndicator.tsx
- [x] T209 [P] [US11] Create DateTimePicker component in frontend/components/common/DateTimePicker.tsx
- [x] T210 [US11] Add due date fields to TaskForm component
- [x] T211 [US11] Implement relative time display ("Due in 3 days", "Overdue by 2 days")
- [x] T212 [US11] Add visual indicators (red for overdue, yellow for due today) in TaskItem
- [x] T213 [US11] Show overdue task count in dashboard header

**Integration**:
- [x] T214 [US11] Wire up DueDateIndicator in TaskItem component
- [x] T215 [US11] Test overdue tasks show in red with "Overdue" label
- [x] T216 [US11] Test tasks due today show in yellow with "Due today" label
- [x] T217 [US11] Test due time validation (requires due date) in form
- [x] T218 [US11] Test filter by "Overdue" shows only overdue tasks

**Checkpoint**: Users can now manage tasks with due dates and receive visual reminders

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T219 [P] Add loading states (skeletons) for all async operations in frontend
- [x] T220 [P] Add error boundaries for React components in frontend/app/error.tsx
- [ ] T221 [P] Implement responsive design for mobile (320px-768px) across all components
- [x] T222 [P] Add keyboard shortcuts (Space to toggle, Escape to close modals) in frontend
- [x] T223 [P] Optimize bundle size (code splitting, lazy loading) in Next.js
- [x] T224 [P] Add database indexes for performance (user_id, created_at, due_date) in migration
- [x] T225 [P] Implement API rate limiting (100 req/min per user) in backend middleware
- [x] T226 [P] Add comprehensive API documentation with OpenAPI/Swagger in backend
- [x] T227 [P] Create deployment guide (Vercel for frontend, Railway for backend) in docs/
- [x] T228 [P] Add health check endpoint GET /health in backend/app/api/health.py
- [x] T229 [P] Configure production environment variables template in README.md
- [x] T230 [P] Add CI/CD pipeline (tests, lint, type-check) in .github/workflows/ci.yml
- [ ] T231 Run full test suite (backend >90%, frontend >80% coverage)
- [ ] T232 Run quickstart.md validation (fresh install on clean machine)
- [ ] T233 Perform security audit (SQL injection, XSS, CSRF protection)
- [ ] T234 Performance testing (1000 tasks, 100 concurrent users)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-13)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 14)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Requires US1 for authentication but is independently testable
- **User Story 3 (P1)**: Can start after Foundational - Requires US1 & US2 but is independently testable
- **User Story 4 (P2)**: Requires US2 (task viewing) & US3 (task creation)
- **User Story 5 (P2)**: Requires US2 (task viewing)
- **User Story 6 (P2)**: Requires US2 (task viewing)
- **User Story 7 (P2)**: Requires US2 (task viewing)
- **User Story 8 (P3)**: Requires US2 (task viewing)
- **User Story 9 (P3)**: Requires US2 (task viewing)
- **User Story 10 (P3)**: Requires US3 (task creation) & US5 (completion)
- **User Story 11 (P3)**: Requires US2 (task viewing) & US3 (task creation)

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Backend API before frontend UI
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 Setup**:
- T003 (frontend init) || T002 (backend init)
- T004 (backend lint) || T005 (frontend lint) || T006 (tailwind)
- T007 (backend .env) || T008 (frontend .env) || T009 (CORS) || T010 (.gitignore)

**Phase 2 Foundational**:
- T013 (Alembic) || T014 (Base metadata)
- T016 (Better Auth config) || T017 (API route) || T018 (User model)
- T022 (JWT middleware) || T023 (get_current_user) || T024 (exception handler) || T025 (error schemas)
- T027 (pytest fixtures) || T028 (Jest config) || T029 (RTL) || T030 (API utils)

**User Stories (after Foundational)**:
All user stories can be worked on in parallel by different team members:
- Developer A: US1 (Authentication)
- Developer B: US2 (View Tasks)
- Developer C: US3 (Create Tasks)
- Continue pattern for US4-US11

**Within Each Story - Tests**:
- All test tasks marked [P] can run in parallel
- Example US1: T031 || T032 || T033 || T034

**Within Each Story - Models**:
- All model tasks marked [P] can run in parallel
- Example US2: T055 (Task model) || T056 (TaskResponse schema)

**Within Each Story - Frontend Components**:
- All component tasks marked [P] can run in parallel
- Example US2: T063 (dashboard) || T064 (layout) || T065 (TaskList) || T066 (TaskItem) || T067 (EmptyState)

**Phase 14 Polish**:
- All tasks marked [P] can run in parallel (documentation, testing, optimization)

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T030) - **CRITICAL BLOCKING PHASE**
3. Complete Phase 3: US1 Authentication (T031-T050)
4. **STOP and VALIDATE**: Test US1 independently (users can register and login)
5. Complete Phase 4: US2 View Tasks (T051-T073)
6. **STOP and VALIDATE**: Test US2 independently (users can see their tasks)
7. Complete Phase 5: US3 Create Tasks (T074-T095)
8. **STOP and VALIDATE**: Test US3 independently (users can add tasks)
9. **MVP READY**: Deploy and demo core functionality (auth + view + create)

**MVP Delivers**: Secure multi-user task viewing and creation - immediately usable

### Incremental Delivery (Add Features Progressively)

1. MVP (US1-US3) → Deploy → Get feedback
2. Add US4 Edit Tasks → Deploy → Get feedback
3. Add US5 Complete Tasks → Deploy → Get feedback
4. Add US6 Delete Tasks → Deploy → Get feedback
5. Add US7-US11 (P2-P3 features) as needed based on user feedback

### Parallel Team Strategy (3+ Developers)

**Week 1-2: Foundation (Everyone Together)**
- Team completes Setup (Phase 1) together
- Team completes Foundational (Phase 2) together - **CRITICAL PATH**

**Week 3-4: Parallel User Stories**
Once Foundational is done:
- Developer A: US1 Authentication (T031-T050)
- Developer B: US2 View Tasks (T051-T073)
- Developer C: US3 Create Tasks (T074-T095)

**Week 5-6: More Parallel Stories**
- Developer A: US4 Update + US5 Complete
- Developer B: US6 Delete + US7 Filter
- Developer C: US8 Search + US9 Sort

**Week 7-8: Advanced Features + Polish**
- Developer A: US10 Recurring Tasks
- Developer B: US11 Due Dates
- Developer C: Phase 14 Polish

**Advantage**: 3x faster delivery with parallel development after foundation

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **TDD Approach**: Tests MUST be written first and FAIL before implementation per constitution
- **Each user story**: Should be independently completable and testable
- **Commit frequency**: Commit after each task or logical group
- **Validation checkpoints**: Stop after each user story to test independently
- **Coverage targets**: >90% backend (pytest), >80% frontend (Jest)
- **Foundational phase (Phase 2)**: BLOCKS all user stories - must complete first
- **MVP = US1-US3**: Authentication + View + Create = minimum viable product
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 234
**Setup (Phase 1)**: 10 tasks
**Foundational (Phase 2)**: 20 tasks (BLOCKING)
**User Story 1 (P1)**: 20 tasks (Authentication)
**User Story 2 (P1)**: 23 tasks (View Tasks)
**User Story 3 (P1)**: 22 tasks (Create Tasks)
**User Story 4 (P2)**: 17 tasks (Update Tasks)
**User Story 5 (P2)**: 15 tasks (Complete Tasks)
**User Story 6 (P2)**: 17 tasks (Delete Tasks)
**User Story 7 (P2)**: 15 tasks (Filter Tasks)
**User Story 8 (P3)**: 14 tasks (Search Tasks)
**User Story 9 (P3)**: 14 tasks (Sort Tasks)
**User Story 10 (P3)**: 15 tasks (Recurring Tasks)
**User Story 11 (P3)**: 16 tasks (Due Dates)
**Polish (Phase 14)**: 16 tasks

**Parallel Opportunities**: 87 tasks marked [P] can run in parallel within their phase
**MVP Scope**: 75 tasks (Setup + Foundational + US1 + US2 + US3)
**Estimated MVP Timeline**: 2-3 weeks for single developer, 1-2 weeks for team of 3

---

**Ready for implementation! Each task is specific and executable with clear file paths.**
