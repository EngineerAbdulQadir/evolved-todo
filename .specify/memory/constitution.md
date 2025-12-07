<!--
Sync Impact Report:
Version: 1.1.0 (MINOR - Expanded Phase 1 scope)
Previous Version: 1.0.1
Changes in v1.1.0:
  - EXPANDED Phase 1 scope from 5 features to 10 features
  - Added Intermediate Level features (6-8): Priorities/Tags, Search/Filter, Sort
  - Added Advanced Level features (9-10): Recurring Tasks, Due Dates/Reminders
  - Updated YAGNI Principle to reflect comprehensive feature set
  - Maintained Phase 1 constraints: in-memory only, CLI only, single-user
Principles (Updated):
  - I. Spec-First Development (unchanged)
  - II. Test-First (TDD - NON-NEGOTIABLE) (unchanged)
  - III. YAGNI Principle (UPDATED - now includes 10 features across 3 levels)
  - IV. Technology Stack Requirements (unchanged)
  - V. Clean Code & Modularity (unchanged)
  - VI. Type Safety (unchanged)
  - VII. Comprehensive Documentation (unchanged)
  - VIII. Error Handling (unchanged)
Templates Requiring Updates: None (scope expansion, not structural change)
Follow-up TODOs: Create specifications for all 10 features
-->

# Evolved Todo - Phase 1 Constitution

## Core Principles

### I. Spec-First Development
Every feature MUST have a specification written and approved before implementation begins. Specifications are the single source of truth for requirements, acceptance criteria, and implementation guidance.

**Rules:**
- Feature specs live in `specs/<feature>/spec.md`
- All specs follow the spec-template structure
- Specs must define clear acceptance criteria
- Implementation must not begin until spec is approved
- Code that doesn't match spec is incorrect, regardless of functionality

**Rationale:** Spec-first ensures alignment between architect (human or AI), developer (Claude Code), and stakeholder expectations before any code is written.

### II. Test-First (TDD - NON-NEGOTIABLE)
Test-Driven Development is mandatory. Tests MUST be written, reviewed, and approved before implementation code.

**Red-Green-Refactor Cycle (Strictly Enforced):**
1. **Red:** Write failing tests that capture acceptance criteria
2. **Green:** Implement minimal code to pass tests
3. **Refactor:** Improve code while keeping tests green

**Rules:**
- Tests written first → User approved → Tests fail → Then implement
- All public functions must have unit tests
- Edge cases and error paths must have tests
- Tests must be deterministic and isolated
- Integration tests required for inter-module communication

**Rationale:** TDD ensures correctness, prevents regression, and serves as executable documentation.

### III. YAGNI Principle (Phase 1 Scope)
"You Aren't Gonna Need It" - Only implement the specified Phase 1 features (Basic, Intermediate, and Advanced levels). No additional features beyond this list, no premature optimization, no speculative functionality.

**Phase 1 Features - Basic Level (Core Essentials):**
1. Add Task – Create new todo items
2. Delete Task – Remove tasks from the list
3. Update Task – Modify existing task details
4. View Task List – Display all tasks
5. Mark as Complete – Toggle task completion status

**Phase 1 Features - Intermediate Level (Organization & Usability):**
6. Priorities & Tags/Categories – Assign levels (high/medium/low) or labels (work/home)
7. Search & Filter – Search by keyword; filter by status, priority, or date
8. Sort Tasks – Reorder by due date, priority, or alphabetically

**Phase 1 Features - Advanced Level (Intelligent Features):**
9. Recurring Tasks – Auto-reschedule repeating tasks (e.g., "weekly meeting")
10. Due Dates & Time Reminders – Set deadlines with date/time pickers; notifications

**Still Forbidden in Phase 1:**
- ❌ Database or file persistence (in-memory only)
- ❌ User authentication (single-user CLI)
- ❌ Web interface (CLI only)
- ❌ Any feature not in the above 10-feature list

**Rationale:** Comprehensive feature set ensures a fully functional, production-ready CLI todo app while maintaining in-memory simplicity. All features must work together as a cohesive system before transitioning to Phase II (web + database).

### IV. Technology Stack Requirements
Phase 1 MUST use the specified technology stack. No substitutions.

**Mandatory Stack:**
- **Python:** 3.13+ (no older versions)
- **Package Manager:** UV (not pip, not poetry, not conda)
- **Storage:** In-memory only (Python dictionaries, lists)
- **Testing:** pytest
- **Type Checking:** mypy
- **Linting:** ruff

**Rules:**
- All dependencies managed via `pyproject.toml` with UV
- No external databases (SQLite, PostgreSQL, etc.)
- No file I/O for persistence (no JSON files, no pickle)
- Must run without external services or network calls

**Rationale:** Standardization ensures consistency across all hackathon submissions and prepares for Phase II migration.

### V. Clean Code & Modularity
Code MUST be well-organized, modular, and follow clean code principles.

**Organization Requirements:**
- Separation of concerns (data models, business logic, CLI interface)
- Single Responsibility Principle for all functions and classes
- Clear, descriptive naming (no abbreviations like `td`, `lst`, `mgr`)
- Maximum function length: 20 lines (excluding docstrings)
- Maximum file length: 200 lines

**Project Structure:**
```
src/
├── models/          # Data models (Task)
├── services/        # Business logic (TaskService)
├── cli/             # CLI interface
└── main.py          # Entry point
tests/
├── test_models.py
├── test_services.py
└── test_cli.py
```

**Rationale:** Modularity enables testability, maintainability, and smooth transition to Phase II (web application).

### VI. Type Safety
All functions MUST have complete type annotations. Type checking with mypy MUST pass without errors.

**Requirements:**
- Function signatures: parameters and return types fully annotated
- Class attributes: type annotations required
- No `Any` types unless explicitly justified
- Use generic types (`list[Task]`, not `list`)
- Enable strict mypy mode

**Example:**
```python
def add_task(title: str, description: str | None = None) -> Task:
    """Add a new task to the list."""
    # Implementation
```

**Rationale:** Type safety catches bugs at compile time, improves IDE support, and serves as inline documentation.

### VII. Comprehensive Documentation
Documentation MUST be thorough, clear, and maintained alongside code.

**Required Documentation:**
1. **README.md:**
   - Project overview and Phase 1 scope
   - Setup instructions (UV installation, dependencies)
   - Usage examples for all 5 features
   - Running tests

2. **Docstrings (Google style):**
   - All public functions, classes, methods
   - Include Args, Returns, Raises sections
   - Usage examples for complex functions

3. **Architecture Documentation:**
   - `docs/architecture.md` explaining module organization
   - Data flow diagrams (text-based acceptable)
   - Design decisions and rationale

4. **Inline Comments:**
   - Complex logic requiring explanation
   - NOT for self-evident code

**Rationale:** Comprehensive docs enable onboarding, facilitate review, and prepare for Phase II handoff.

### VIII. Error Handling
Errors MUST be handled explicitly and gracefully. No silent failures.

**Requirements:**
- Validate all user inputs before processing
- Raise descriptive exceptions with context
- Use custom exception classes where appropriate
- Handle edge cases explicitly (empty list, invalid ID, etc.)
- CLI must display user-friendly error messages

**Example:**
```python
class TaskNotFoundError(Exception):
    """Raised when attempting to access a non-existent task."""
    pass

def get_task(task_id: int) -> Task:
    if task_id not in tasks:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")
    return tasks[task_id]
```

**Rationale:** Explicit error handling prevents undefined behavior and improves user experience.

## Phase 1 Scope Constraints

### In-Scope
- Command-line interface (CLI) only
- In-memory task storage (Python data structures)
- 5 Basic Level features (Add, Delete, Update, View, Mark Complete)
- Comprehensive test coverage (>90%)
- Clean, modular, well-documented code

### Out-of-Scope
- Web interface (Phase II)
- Database persistence (Phase II)
- User authentication (Phase II)
- Advanced features (Phases III-V)
- Deployment or containerization (Phase IV)

## Development Workflow

### Feature Development Process
1. **Specification:** Write feature spec in `specs/<feature>/spec.md`
2. **Review Spec:** Ensure alignment with constitution and acceptance criteria
3. **Write Tests:** Create failing tests that validate spec requirements
4. **Approve Tests:** Review test coverage and edge cases
5. **Implement:** Write minimal code to pass tests (Red → Green)
6. **Refactor:** Improve code quality while keeping tests green
7. **Documentation:** Update README, docstrings, architecture docs
8. **Final Review:** Verify all quality gates pass

### Iteration Cycle
- Each feature is a single iteration
- No parallel feature development
- Complete one feature fully before starting next
- Order: Add → View → Update → Mark Complete → Delete

## Quality Gates

All quality gates MUST pass before a feature is considered complete.

### Automated Checks (Must Pass)
- ✅ `pytest` - All tests pass
- ✅ `mypy` - No type errors (strict mode)
- ✅ `ruff check` - No linting errors
- ✅ `ruff format --check` - Code formatted correctly
- ✅ Test coverage >90% (measured with pytest-cov)

### Manual Reviews (Must Confirm)
- ✅ Spec requirements met (all acceptance criteria)
- ✅ Constitution compliance (all principles followed)
- ✅ Documentation complete (README, docstrings, architecture)
- ✅ Error handling for edge cases
- ✅ No YAGNI violations (no extra features)

### Pre-Submission Checklist
- [ ] All 5 Basic Level features implemented
- [ ] All quality gates pass
- [ ] README includes setup and usage instructions
- [ ] Architecture documentation explains design
- [ ] Git history shows spec-first + TDD workflow
- [ ] Code runs without errors on clean Python 3.13 + UV environment

## Governance

### Constitution Authority
This constitution supersedes all other practices, preferences, or conventions. When in doubt, the constitution is the tiebreaker.

### Amendment Process
1. Constitution changes require explicit rationale
2. Version increments follow semantic versioning:
   - **MAJOR:** Principle removals or incompatible redefinitions
   - **MINOR:** New principles or significant expansions
   - **PATCH:** Clarifications, typo fixes, non-semantic changes
3. All amendments must update dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Sync Impact Report required for all constitution updates

### Compliance Reviews
- **Per-Feature Review:** Verify spec, tests, implementation, docs against constitution
- **Pre-Submission Review:** Full constitution compliance audit before hackathon submission
- **AI Agent Guidance:** Claude Code must be instructed to validate constitution compliance for all work

### Phase Transition
When transitioning from Phase 1 → Phase 2:
1. Update this same `constitution.md` file (do not create separate files)
2. Increment version to 2.0.0 (MAJOR - phase transition with breaking changes)
3. Update principles to reflect Phase 2 requirements (web app, database, etc.)
4. Document breaking changes in Sync Impact Report at top of file
5. Update Last Amended date
6. Update all dependent templates and guidance for Phase 2 stack
7. Git history will preserve Phase 1 version for reference

**Note:** This constitution is a living document. All phase updates modify this single file with version increments tracked via git.

**Version:** 1.1.0 | **Ratified:** 2025-12-06 | **Last Amended:** 2025-12-06
