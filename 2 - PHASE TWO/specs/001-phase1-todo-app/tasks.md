# Implementation Tasks: Phase 1 Complete Todo App

**Feature**: Phase 1 Todo CLI (10 features)
**Plan**: [plan.md](./plan.md)
**Generated**: 2025-12-06
**Total Tasks**: 87

---

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup & Infrastructure | 8 |
| Phase 2 | Foundation (Blocking) | 10 |
| Phase 3 | US1: Add Task (P1) | 8 |
| Phase 4 | US2: View Tasks (P1) | 7 |
| Phase 5 | US3: Update Task (P1) | 6 |
| Phase 6 | US4: Mark Complete (P1) | 5 |
| Phase 7 | US5: Delete Task (P1) | 5 |
| Phase 8 | US6: Priorities & Tags (P1) | 8 |
| Phase 9 | US7: Search & Filter (P2) | 7 |
| Phase 10 | US8: Due Dates & Reminders (P1) | 8 |
| Phase 11 | US9: Sort Tasks (P2) | 6 |
| Phase 12 | US10: Recurring Tasks (P2) | 6 |
| Phase 13 | Polish & Cross-Cutting | 3 |

---

## Phase 1: Setup & Infrastructure

**Goal**: Initialize project structure and development environment

- [x] T001 Create project directory structure per plan in `src/`, `tests/`, `docs/`
- [x] T002 Initialize UV project with `pyproject.toml` in project root
- [x] T003 [P] Add production dependencies (typer, python-dateutil, rich) to `pyproject.toml`
- [x] T004 [P] Add dev dependencies (pytest, pytest-cov, mypy, ruff) to `pyproject.toml`
- [x] T005 Create `src/__init__.py` with package metadata
- [x] T006 [P] Create `tests/__init__.py` and `tests/conftest.py` with shared fixtures
- [x] T007 [P] Configure mypy strict mode in `pyproject.toml`
- [x] T008 [P] Configure ruff linting rules in `pyproject.toml`

**Parallel Opportunities**: T003-T004, T006-T007-T008 can run in parallel

---

## Phase 2: Foundation (Blocking Prerequisites)

**Goal**: Implement core models, exceptions, and utilities required by all features

**MUST complete before any user story phases**

- [x] T009 Create custom exceptions hierarchy in `src/models/exceptions.py`
- [x] T010 Create Priority enum in `src/models/priority.py`
- [x] T011 [P] Create RecurrencePattern enum in `src/models/recurrence.py`
- [x] T012 [P] Create DueStatus enum in `src/models/priority.py`
- [x] T013 Create IdGenerator class in `src/lib/id_generator.py`
- [x] T014 Create Task dataclass (core attributes only: id, title, description, is_complete, created_at) in `src/models/task.py`
- [x] T015 Add Task validation methods (_validate_title, _validate_description) in `src/models/task.py`
- [x] T016 Create InMemoryTaskStore class in `src/services/task_store.py`
- [x] T017 Create TaskService class with add/get/all methods in `src/services/task_service.py`
- [x] T018 Create CLI app skeleton with typer in `src/main.py`

**Parallel Opportunities**: T010-T011-T012, T013-T014 can run in parallel

---

## Phase 3: US1 - Add Task (P1)

**User Story**: As a user, I want to create new todo items with title and optional description

**Spec**: [001-add-task/spec.md](./001-add-task/spec.md)

**Independent Test**: Create tasks via CLI and verify they appear in task list

### Tasks

- [x] T019 [US1] Write unit tests for TaskService.add() in `tests/unit/test_task_service.py`
- [x] T020 [US1] Implement TaskService.add() with title validation in `src/services/task_service.py`
- [x] T021 [US1] Write unit tests for Task title/description validation in `tests/unit/test_models.py`
- [x] T022 [P] [US1] Implement Task validation for title (1-200 chars, non-empty) in `src/models/task.py`
- [x] T023 [P] [US1] Implement Task validation for description (max 1000 chars) in `src/models/task.py`
- [x] T024 [US1] Create CLI add command with --desc option in `src/cli/commands.py`
- [x] T025 [US1] Write integration tests for `todo add` command in `tests/integration/test_cli_add.py`
- [x] T026 [US1] Add success/error output formatting for add command in `src/cli/formatters.py`

**Parallel Opportunities**: T022-T023 can run in parallel

---

## Phase 4: US2 - View Tasks (P1)

**User Story**: As a user, I want to see all my tasks with their details

**Spec**: [002-view-tasks/spec.md](./002-view-tasks/spec.md)

**Independent Test**: Create multiple tasks, run `todo list`, verify all display correctly

### Tasks

- [x] T027 [US2] Write unit tests for TaskService.all() in `tests/unit/test_task_service.py`
- [x] T028 [US2] Implement TaskService.all() returning sorted by ID in `src/services/task_service.py`
- [x] T029 [US2] Create task display formatter with rich Table in `src/cli/formatters.py`
- [x] T030 [US2] Create CLI list command in `src/cli/commands.py`
- [x] T031 [US2] Handle empty list display with helpful message in `src/cli/formatters.py`
- [x] T032 [US2] Write integration tests for `todo list` command in `tests/integration/test_cli_view.py`
- [x] T033 [US2] Add show command for single task details in `src/cli/commands.py`

---

## Phase 5: US3 - Update Task (P1)

**User Story**: As a user, I want to modify task title and/or description

**Spec**: [003-update-task/spec.md](./003-update-task/spec.md)

**Independent Test**: Create task, update it, verify changes persist

### Tasks

- [x] T034 [US3] Write unit tests for TaskService.update() in `tests/unit/test_task_service.py`
- [x] T035 [US3] Implement TaskService.update() with validation in `src/services/task_service.py`
- [x] T036 [US3] Create CLI update command with --title, --desc options in `src/cli/commands.py`
- [x] T037 [US3] Implement partial update logic (update only provided fields) in `src/services/task_service.py`
- [x] T038 [US3] Write integration tests for `todo update` command in `tests/integration/test_cli_update.py`
- [x] T039 [US3] Add update success/error output in `src/cli/formatters.py`

---

## Phase 6: US4 - Mark Complete (P1)

**User Story**: As a user, I want to toggle task completion status

**Spec**: [004-mark-complete/spec.md](./004-mark-complete/spec.md)

**Independent Test**: Create task, mark complete, verify status toggle

### Tasks

- [x] T040 [US4] Write unit tests for TaskService.toggle_complete() in `tests/unit/test_task_service.py`
- [x] T041 [US4] Implement TaskService.toggle_complete() in `src/services/task_service.py`
- [x] T042 [US4] Create CLI complete command in `src/cli/commands.py`
- [x] T043 [US4] Update task list display with completion indicators ([✓]/[ ]) in `src/cli/formatters.py`
- [x] T044 [US4] Write integration tests for `todo complete` command in `tests/integration/test_cli_complete.py`

---

## Phase 7: US5 - Delete Task (P1)

**User Story**: As a user, I want to remove tasks from my list

**Spec**: [005-delete-task/spec.md](./005-delete-task/spec.md)

**Independent Test**: Create task, delete it, verify not in list

### Tasks

- [x] T045 [US5] Write unit tests for TaskService.delete() in `tests/unit/test_task_service.py`
- [x] T046 [US5] Implement TaskService.delete() in `src/services/task_service.py`
- [x] T047 [US5] Create CLI delete command with --force option in `src/cli/commands.py`
- [x] T048 [US5] Implement confirmation prompt (skip with --force) in `src/cli/commands.py`
- [x] T049 [US5] Write integration tests for `todo delete` command in `tests/integration/test_cli_delete.py`

---

## Phase 8: US6 - Priorities & Tags (P1)

**User Story**: As a user, I want to assign priority levels and tags to tasks

**Spec**: [006-priorities-tags/spec.md](./006-priorities-tags/spec.md)

**Independent Test**: Create task with priority/tags, verify display and updates

### Tasks

- [x] T050 [US6] Extend Task dataclass with priority and tags attributes in `src/models/task.py`
- [x] T051 [US6] Add _validate_tags() method to Task in `src/models/task.py`
- [x] T052 [US6] Write unit tests for priority/tags validation in `tests/unit/test_models.py`
- [x] T053 [US6] Update TaskService.add() to accept priority/tags in `src/services/task_service.py`
- [x] T054 [US6] Update CLI add command with --priority, --tags options in `src/cli/commands.py`
- [x] T055 [US6] Update CLI update command with --priority, --add-tag, --remove-tag in `src/cli/commands.py`
- [x] T056 [US6] Update task list display to show priority and tags in `src/cli/formatters.py`
- [x] T057 [US6] Write integration tests for priority/tags in `tests/integration/test_cli_priority_tags.py`

---

## Phase 9: US7 - Search & Filter (P2)

**User Story**: As a user, I want to search and filter tasks by various criteria

**Spec**: [007-search-filter/spec.md](./007-search-filter/spec.md)

**Independent Test**: Create tasks with different attributes, search/filter, verify results

### Tasks

- [x] T058 [US7] Create SearchService with search_by_keyword() in `src/services/search_service.py`
- [x] T059 [US7] Add filter_tasks() method to SearchService in `src/services/search_service.py`
- [x] T060 [US7] Write unit tests for SearchService in `tests/unit/test_search_service.py`
- [x] T061 [US7] Update CLI list command with --search, --status, --priority, --tag options in `src/cli/commands.py`
- [x] T062 [US7] Implement combined filter logic (AND) in `src/services/search_service.py`
- [x] T063 [US7] Add filtered task count display ("Showing X of Y tasks") in `src/cli/formatters.py`
- [x] T064 [US7] Write integration tests for search/filter in `tests/integration/test_cli_search_filter.py`

---

## Phase 10: US8 - Due Dates & Reminders (P1)

**User Story**: As a user, I want to set due dates and see overdue notifications

**Spec**: [010-due-dates-reminders/spec.md](./010-due-dates-reminders/spec.md)

**Independent Test**: Create task with due date, verify overdue detection

### Tasks

- [x] T065 [US8] Extend Task with due_date, due_time attributes in `src/models/task.py`
- [x] T066 [US8] Add is_overdue and due_status computed properties to Task in `src/models/task.py`
- [x] T067 [US8] Create date_parser module with parse_due_date(), parse_due_time() in `src/lib/date_parser.py`
- [x] T068 [US8] Write unit tests for date parsing in `tests/unit/test_date_parser.py`
- [x] T069 [US8] Update CLI add/update commands with --due, --time options in `src/cli/commands.py`
- [x] T070 [US8] Update task list display with due dates and overdue indicators in `src/cli/formatters.py`
- [x] T071 [US8] Add CLI notifications for overdue/due-today tasks in `src/cli/formatters.py`
- [x] T072 [US8] Write integration tests for due dates in `tests/integration/test_cli_due_dates.py`

---

## Phase 11: US9 - Sort Tasks (P2)

**User Story**: As a user, I want to sort tasks by priority, due date, or title

**Spec**: [008-sort-tasks/spec.md](./008-sort-tasks/spec.md)

**Independent Test**: Create tasks, sort by different criteria, verify order

### Tasks

- [x] T073 [US9] Create SortService with sort_tasks() in `src/services/sort_service.py`
- [x] T074 [US9] Implement sort by priority, due date, title, id in `src/services/sort_service.py`
- [x] T075 [US9] Write unit tests for SortService in `tests/unit/test_sort_service.py`
- [x] T076 [US9] Update CLI list command with --sort, --desc options in `src/cli/commands.py`
- [x] T077 [US9] Add current sort order indicator to display in `src/cli/formatters.py`
- [x] T078 [US9] Write integration tests for sorting in `tests/integration/test_cli_sort.py`

---

## Phase 12: US10 - Recurring Tasks (P2)

**User Story**: As a user, I want tasks to auto-reschedule when completed

**Spec**: [009-recurring-tasks/spec.md](./009-recurring-tasks/spec.md)

**Independent Test**: Create recurring task, complete it, verify new occurrence

### Tasks

- [x] T079 [US10] Extend Task with recurrence, recurrence_day attributes in `src/models/task.py`
- [x] T080 [US10] Create RecurrenceService with calculate_next_occurrence() in `src/services/recurrence_service.py`
- [x] T081 [US10] Write unit tests for RecurrenceService (edge cases: month boundaries) in `tests/unit/test_recurrence_service.py`
- [x] T082 [US10] Update TaskService.toggle_complete() to create new occurrence for recurring tasks in `src/services/task_service.py`
- [x] T083 [US10] Update CLI add/update commands with --recur, --recur-day options in `src/cli/commands.py`
- [x] T084 [US10] Write integration tests for recurring tasks in `tests/integration/test_cli_recurring.py`

---

## Phase 13: Polish & Cross-Cutting Concerns

**Goal**: Final quality checks and documentation

- [x] T085 Create README.md with installation, usage, and examples in project root
- [x] T086 Run full test suite with coverage (`pytest --cov --cov-fail-under=90`)
- [x] T087 Run quality checks (`mypy --strict`, `ruff check`, `ruff format --check`)

---

## Dependency Graph

```
Phase 1 (Setup) ──► Phase 2 (Foundation) ──┬──► Phase 3 (US1: Add)
                                           │
                                           └──► Phase 4 (US2: View)
                                                      │
                              ┌────────────────────────┤
                              ▼                        ▼
                    Phase 5 (US3: Update)    Phase 6 (US4: Complete)
                              │                        │
                              ▼                        ▼
                    Phase 7 (US5: Delete)    Phase 8 (US6: Priority/Tags)
                              │                        │
                              └──────────┬─────────────┘
                                         ▼
                              Phase 9 (US7: Search/Filter)
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                    Phase 10 (US8: Due Dates)  Phase 11 (US9: Sort)
                              │                     │
                              └──────────┬──────────┘
                                         ▼
                              Phase 12 (US10: Recurring)
                                         │
                                         ▼
                              Phase 13 (Polish)
```

---

## Parallel Execution Opportunities

### Within Phases

| Phase | Parallel Tasks |
|-------|----------------|
| Phase 1 | T003+T004, T006+T007+T008 |
| Phase 2 | T010+T011+T012, T013+T014 |
| Phase 3 | T022+T023 |

### Across Phases (after Foundation)

- **US1 + US2**: Can develop in parallel (both only need Foundation)
- **US3 + US4 + US5**: Can develop in parallel after US1+US2
- **US6 + US7**: Can develop in parallel after US3-US5
- **US8 + US9**: Can develop in parallel after US6-US7

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4**

With just these phases complete, users can:
- Add tasks with title and description
- View all tasks in a list
- Verify the app works end-to-end

### Incremental Delivery Order

1. **Week 1**: Setup → Foundation → Add → View (MVP)
2. **Week 2**: Update → Complete → Delete (Basic CRUD complete)
3. **Week 3**: Priorities/Tags → Search/Filter (Intermediate features)
4. **Week 4**: Due Dates → Sort → Recurring (Advanced features)
5. **Final**: Polish & Documentation

---

## Quality Gates (Per Phase)

Each phase must pass before moving to the next:

- [x] All phase tasks completed
- [x] Unit tests passing for new code
- [x] Integration tests passing for CLI commands
- [x] `mypy --strict` passes
- [x] `ruff check` passes
- [x] Code coverage maintained >90%
