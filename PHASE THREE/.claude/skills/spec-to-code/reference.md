# Spec-to-Code Reference

Comprehensive guide for implementing features following Spec-Driven Development (SDD) methodology.

## Table of Contents

1. [SDD Methodology](#sdd-methodology)
2. [Spec Document Structure](#spec-document-structure)
3. [Acceptance Criteria Patterns](#acceptance-criteria-patterns)
4. [Traceability Techniques](#traceability-techniques)
5. [Implementation Order](#implementation-order)
6. [Contract-Driven Development](#contract-driven-development)
7. [Edge Case Discovery](#edge-case-discovery)
8. [Testing Strategy from Specs](#testing-strategy-from-specs)

---

## SDD Methodology

### Core Principles

**Spec-Driven Development (SDD)** means:
1. **Specification First**: Write detailed spec before any code
2. **Acceptance Criteria Drive Tests**: Every AC becomes at least one test
3. **Traceability**: Every line of code/test references the spec
4. **Contract Adherence**: Implementation must match spec contracts exactly
5. **Spec is Truth**: Code is verified against spec, not vice versa

### SDD Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. READ SPEC                                                 │
│    - User story & goals                                      │
│    - Acceptance criteria (ACs)                               │
│    - Technical contracts (models, APIs, CLI)                 │
│    - Edge cases & error scenarios                            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. MAP ACCEPTANCE CRITERIA                                   │
│    - AC1 → test_scenario_1()                                 │
│    - AC2 → test_scenario_2()                                 │
│    - AC3 → test_edge_case_1()                                │
│    - Create traceability matrix                              │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GENERATE TEST STUBS                                       │
│    - One test per AC (minimum)                               │
│    - Include spec references in docstrings                   │
│    - Add TODO comments for implementation                    │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. IMPLEMENT (TDD)                                           │
│    - Red: Run failing test                                   │
│    - Green: Minimal code to pass                             │
│    - Refactor: Improve while keeping tests green             │
│    - Repeat for each AC                                      │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. VERIFY AGAINST SPEC                                       │
│    - All ACs have passing tests                              │
│    - Contracts match spec exactly                            │
│    - Edge cases handled                                      │
│    - Error messages user-friendly                            │
└─────────────────────────────────────────────────────────────┘
```

### SDD vs Traditional Development

| Aspect | Traditional | Spec-Driven Development |
|--------|-------------|------------------------|
| Starting point | Code idea | Written specification |
| Requirements | Informal/verbal | Formal acceptance criteria |
| Testing | After implementation | Derived from ACs before code |
| Traceability | Ad-hoc comments | Systematic spec references |
| Verification | "Does it work?" | "Does it match spec?" |
| Changes | Update code first | Update spec first, then code |

---

## Spec Document Structure

### Standard Spec Sections

Every spec should contain:

#### 1. User Story
```markdown
## User Story

**As a** [user role]
**I want** [goal/desire]
**So that** [benefit/value]

**Priority**: P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
```

**Example:**
```markdown
**As a** todo app user
**I want** to create tasks with a title and optional description
**So that** I can track things I need to do

**Priority**: P1 (High)
```

#### 2. Acceptance Criteria

```markdown
## Acceptance Criteria

- **AC1**: [Observable behavior that must be true]
- **AC2**: [Another testable requirement]
- **AC3**: [Edge case handling]
- **AC4**: [Error scenario]
```

**Characteristics of Good ACs:**
- **Observable**: Can be verified by running the system
- **Testable**: Can write automated test
- **Unambiguous**: Only one interpretation
- **Independent**: Don't overlap with other ACs
- **Complete**: Cover all scenarios (happy path + errors)

**Example:**
```markdown
## Acceptance Criteria

- **AC1**: User can create task with just a title
- **AC2**: User can optionally add description when creating task
- **AC3**: Title must be 1-200 characters (validation error if violated)
- **AC4**: Description max 1000 characters (validation error if violated)
- **AC5**: System generates unique sequential ID for each task
- **AC6**: Task is marked incomplete by default
- **AC7**: Creation timestamp is recorded automatically
```

#### 3. Technical Contracts

##### 3.1 Data Models
```markdown
## Data Models

### Task
```python
@dataclass
class Task:
    id: int                           # Sequential, auto-generated
    title: str                        # Required, 1-200 chars
    description: Optional[str] = None # Optional, max 1000 chars
    is_complete: bool = False         # Default: incomplete
    created_at: datetime              # Auto-generated
```

**Validation Rules:**
- Title: Non-empty, 1-200 characters, strip whitespace
- Description: If provided, max 1000 characters
```

##### 3.2 Service Contract
```markdown
## Service API

### TaskService.add()
```python
def add(
    self,
    title: str,
    description: Optional[str] = None
) -> Task:
    """
    Create new task with validation.

    Args:
        title: Task title (1-200 chars, non-empty after strip)
        description: Optional description (max 1000 chars)

    Returns:
        Created task with generated ID and timestamp

    Raises:
        ValidationError: If title/description violate constraints
    """
```

**Behavior:**
- Generates next sequential ID
- Strips whitespace from title
- Validates title length (1-200)
- Validates description length if provided (max 1000)
- Sets is_complete = False
- Sets created_at = current timestamp
- Saves to storage
- Returns created Task
```

##### 3.3 CLI Contract
```markdown
## CLI Interface

### Command: `todo add`
```bash
todo add <title> [--desc <description>]
```

**Arguments:**
- `<title>`: Required positional argument, task title

**Options:**
- `--desc <text>`, `-d <text>`: Optional description

**Success Output:**
```
✓ Task #1 created: Buy milk
```

**Error Output:**
```
Error: Title cannot be empty
Error: Title cannot exceed 200 characters
Error: Description cannot exceed 1000 characters
```

**Exit Codes:**
- 0: Success
- 1: Validation error
```

#### 4. Edge Cases & Error Scenarios

```markdown
## Edge Cases

### Valid Edge Cases (Should Work)
1. Title with exactly 1 character
2. Title with exactly 200 characters
3. Description with exactly 1000 characters
4. Title with leading/trailing whitespace (should be stripped)
5. Description is empty string (treated as None)

### Invalid Cases (Should Fail with ValidationError)
1. Empty title or whitespace-only title
2. Title with 201+ characters
3. Description with 1001+ characters
4. Title is None (type error, caught by type checker)

### Boundary Testing
- Title length: 0 (fail), 1 (pass), 200 (pass), 201 (fail)
- Description length: 1000 (pass), 1001 (fail)
```

---

## Acceptance Criteria Patterns

### Pattern 1: Happy Path AC

**Template:**
```markdown
- **AC[N]**: User can [perform action] [under normal conditions]
```

**Example:**
```markdown
- **AC1**: User can create task with just a title
```

**Test Mapping:**
```python
def test_create_task_with_title_only():  # AC1
    """User can create task with just a title (AC1)."""
    task = task_service.add(title="Buy milk")

    assert task.id == 1
    assert task.title == "Buy milk"
    assert task.description is None
    assert task.is_complete is False
    assert task.created_at is not None
```

### Pattern 2: Optional Feature AC

**Template:**
```markdown
- **AC[N]**: User can optionally [perform optional action]
```

**Example:**
```markdown
- **AC2**: User can optionally add description when creating task
```

**Test Mapping:**
```python
def test_create_task_with_description():  # AC2
    """User can optionally add description (AC2)."""
    task = task_service.add(title="Buy milk", description="From store")

    assert task.description == "From store"
```

### Pattern 3: Validation AC

**Template:**
```markdown
- **AC[N]**: [Field] must [constraint] (validation error if violated)
```

**Example:**
```markdown
- **AC3**: Title must be 1-200 characters (validation error if violated)
```

**Test Mapping (Multiple Tests):**
```python
def test_title_min_length_validation():  # AC3 (lower bound)
    """Title must be at least 1 character (AC3)."""
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        task_service.add(title="")

def test_title_max_length_validation():  # AC3 (upper bound)
    """Title cannot exceed 200 characters (AC3)."""
    long_title = "x" * 201
    with pytest.raises(ValidationError, match="cannot exceed 200 characters"):
        task_service.add(title=long_title)

def test_title_exactly_max_length_is_valid():  # AC3 (boundary)
    """Title with exactly 200 characters is valid (AC3)."""
    title = "x" * 200
    task = task_service.add(title=title)
    assert task.title == title
```

### Pattern 4: System Behavior AC

**Template:**
```markdown
- **AC[N]**: System [automatically performs action]
```

**Example:**
```markdown
- **AC5**: System generates unique sequential ID for each task
```

**Test Mapping:**
```python
def test_sequential_id_generation():  # AC5
    """System generates unique sequential IDs (AC5)."""
    task1 = task_service.add(title="Task 1")
    task2 = task_service.add(title="Task 2")
    task3 = task_service.add(title="Task 3")

    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3
    assert task2.id == task1.id + 1
    assert task3.id == task2.id + 1
```

### Pattern 5: Default Value AC

**Template:**
```markdown
- **AC[N]**: [Field] defaults to [value] if not provided
```

**Example:**
```markdown
- **AC6**: Task is marked incomplete by default
```

**Test Mapping:**
```python
def test_task_incomplete_by_default():  # AC6
    """Task is marked incomplete by default (AC6)."""
    task = task_service.add(title="New task")
    assert task.is_complete is False
```

### Pattern 6: Integration AC

**Template:**
```markdown
- **AC[N]**: [Component A] integrates with [Component B] to [achieve result]
```

**Example:**
```markdown
- **AC8**: CLI command displays success message with task ID and title
```

**Test Mapping:**
```python
def test_cli_add_displays_success_message():  # AC8
    """CLI displays success with ID and title (AC8)."""
    result = runner.invoke(app, ["add", "Buy milk"])

    assert result.exit_code == 0
    assert "✓" in result.stdout or "created" in result.stdout.lower()
    assert "#1" in result.stdout
    assert "Buy milk" in result.stdout
```

---

## Traceability Techniques

### 1. Spec References in Tests

**Format:** `(Spec: <feature-id> section <section-number>)`

```python
def test_title_validation():
    """Title must be 1-200 characters (Spec: 001-add-task section 2.1)."""
    with pytest.raises(ValidationError):
        task_service.add(title="")
```

### 2. AC Tags in Tests

**Format:** `# AC[N]` or `(AC[N])`

```python
def test_create_with_description():  # AC2
    """User can optionally add description when creating task."""
    task = task_service.add(title="Buy milk", description="From store")
    assert task.description == "From store"
```

### 3. Spec References in Code

```python
def add(self, title: str, description: Optional[str] = None) -> Task:
    """
    Create new task with validation (Spec: 001-add-task section 3.1).

    Implements:
        - AC1: Create with title only
        - AC2: Optional description
        - AC3: Title validation (1-200 chars)
        - AC4: Description validation (max 1000 chars)
        - AC5: Sequential ID generation
    """
    # AC5: Generate sequential ID (Spec: 001-add-task section 3.1.2)
    task_id = self._id_gen.next()

    # AC3, AC4: Task validates itself in __post_init__
    task = Task(id=task_id, title=title, description=description)

    self._store.save(task)
    return task
```

### 4. Traceability Matrix

Create `traceability-matrix.md` for each feature:

```markdown
# Traceability Matrix: Add Task Feature

| AC | Description | Tests | Code |
|----|-------------|-------|------|
| AC1 | Create with title only | `test_create_task_with_title_only()` | `TaskService.add():93` |
| AC2 | Optional description | `test_create_task_with_description()` | `TaskService.add():93` |
| AC3 | Title validation | `test_title_min_length()`, `test_title_max_length()` | `Task._validate_title():62` |
| AC4 | Description validation | `test_description_max_length()` | `Task._validate_description():68` |
| AC5 | Sequential IDs | `test_sequential_id_generation()` | `TaskService.add():95` |
| AC6 | Default incomplete | `test_task_incomplete_by_default()` | `Task:43` |
| AC7 | Auto timestamp | `test_created_at_auto_generated()` | `Task:44` |
| AC8 | CLI success message | `test_cli_add_success_message()` | `commands.add_task():115` |
```

---

## Implementation Order

### Dependency-Ordered Implementation

```
Layer 3: CLI Layer
    ↑ depends on
Layer 2: Service Layer
    ↑ depends on
Layer 1: Model Layer
    ↑ depends on
Layer 0: Utilities (ID generator, storage)
```

**Implementation Order:**
1. **Utilities first** (no dependencies)
2. **Models second** (depend on utilities)
3. **Services third** (depend on models + utilities)
4. **CLI last** (depend on services + models)

### Task-Level Implementation Order (Example: US1 Add Task)

From `tasks.md`:

```markdown
## Phase 3: US1 - Add Task (P1)

### Step 1: Utilities (T009-T018)
- [x] T009: Create IdGenerator class
- [x] T010: Write tests for IdGenerator
- [x] T011: Create InMemoryTaskStore class
- [x] T012: Write tests for InMemoryTaskStore

### Step 2: Models (T019-T023)
- [ ] T019: Write unit tests for Task validation (AC3, AC4)
- [ ] T020: Implement Task dataclass with validation (AC3, AC4)
- [ ] T021: Write tests for Task defaults (AC6, AC7)
- [ ] T022: Implement Task defaults (AC6, AC7)

### Step 3: Services (T024-T028)
- [ ] T024: Write unit tests for TaskService.add() (AC1, AC2, AC5)
- [ ] T025: Implement TaskService.add() (AC1, AC2, AC5)

### Step 4: CLI (T029-T033)
- [ ] T029: Write integration tests for CLI add command (AC8)
- [ ] T030: Implement CLI add command (AC8)
- [ ] T031: Add output formatter for success messages
```

---

## Contract-Driven Development

### CLI Contract First

**From Spec:**
```bash
todo add <title> [--desc <description>]
```

**Create Contract Document:** `contracts/cli-commands.md`

```markdown
## `todo add`

**Signature:**
```bash
todo add <title> [--desc <description>]
```

**Type Signature:**
```python
def add_task(
    title: str,                    # Required positional
    desc: Optional[str] = None     # Optional flag
) -> None
```

**Behavior:**
- Calls `task_service.add(title, description=desc)`
- On success: Print success message, exit 0
- On ValidationError: Print error, exit 1
- On unexpected error: Print generic error, exit 2

**Output Contract:**
```
Success: "✓ Task #<id> created: <title>"
Error:   "Error: <message>"
```
```

### Service Contract

**From Spec:**
```python
def add(title: str, description: Optional[str] = None) -> Task
```

**Contract Guarantees:**
- **Input**: Accepts title (str) and optional description (str)
- **Output**: Returns Task with all fields populated
- **Side Effects**: Task saved to storage
- **Errors**: Raises ValidationError if constraints violated
- **Idempotency**: Not idempotent (creates new task each call)

### Model Contract

**From Spec:**
```python
@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Contract Guarantees:**
- **Validation**: Raises ValidationError in `__post_init__` if invalid
- **Immutability**: Fields can be modified after creation (mutable)
- **Defaults**: `is_complete` defaults to False, `created_at` auto-generated

---

## Edge Case Discovery

### Systematic Edge Case Discovery

For each field in the model, ask:

1. **Boundaries**: What are min/max values?
2. **Special Values**: What about None, empty string, whitespace?
3. **Type Mismatches**: What if wrong type provided?
4. **Encoding**: Unicode, special characters, emojis?
5. **Length**: Extremely short/long values?

**Example: Task.title**

| Category | Test Case | Expected |
|----------|-----------|----------|
| Boundary | Title with 1 char | ✅ Valid |
| Boundary | Title with 200 chars | ✅ Valid |
| Boundary | Title with 0 chars (empty) | ❌ ValidationError |
| Boundary | Title with 201 chars | ❌ ValidationError |
| Special | Title with only whitespace | ❌ ValidationError (stripped = empty) |
| Special | Title with leading/trailing spaces | ✅ Valid (stripped) |
| Encoding | Title with emojis | ✅ Valid |
| Encoding | Title with Unicode characters | ✅ Valid |
| Type | Title is None | ❌ TypeError (caught by mypy) |
| Type | Title is int | ❌ TypeError (caught by mypy) |

---

## Testing Strategy from Specs

### Test Pyramid for Each Feature

```
        ┌─────────────────┐
        │  E2E Tests (1)  │  Full system, CLI to storage
        ├─────────────────┤
        │ Integration (3) │  CLI + Service, Service + Model
        ├─────────────────┤
        │   Unit Tests    │  Models, Services in isolation
        │      (10+)      │
        └─────────────────┘
```

### Test Categories from Spec

**From Acceptance Criteria:**

1. **Happy Path Tests** (Green path)
   - One test per primary AC
   - Example: AC1 → test_create_task_with_title_only()

2. **Validation Tests** (Error path)
   - One test per validation rule
   - Test both boundaries (min, max)
   - Example: AC3 → test_title_min_length(), test_title_max_length()

3. **Integration Tests** (CLI + Service)
   - One test per CLI command
   - Example: AC8 → test_cli_add_command()

4. **Edge Case Tests** (Boundary conditions)
   - Derived from edge case analysis
   - Example: test_title_with_exactly_200_chars()

### Example Test Suite Structure

**For US1 (Add Task):**

```
tests/
├── unit/
│   ├── test_task_model.py
│   │   ├── test_valid_task_creation()           # AC1, AC2
│   │   ├── test_title_cannot_be_empty()         # AC3
│   │   ├── test_title_max_length()              # AC3
│   │   ├── test_description_max_length()        # AC4
│   │   ├── test_task_defaults_incomplete()      # AC6
│   │   └── test_created_at_auto_generated()     # AC7
│   │
│   └── test_task_service.py
│       ├── test_add_task_with_title()           # AC1
│       ├── test_add_task_with_description()     # AC2
│       ├── test_sequential_id_generation()      # AC5
│       └── test_add_task_validation_error()     # AC3, AC4
│
└── integration/
    └── test_cli_add.py
        ├── test_add_command_success()           # AC8
        ├── test_add_command_with_description()  # AC8
        └── test_add_command_validation_error()  # AC8
```

**Coverage Mapping:**
- AC1: 3 tests (model, service, CLI)
- AC2: 3 tests (model, service, CLI)
- AC3: 3 tests (model validation, service, CLI error)
- AC4: 3 tests (model validation, service, CLI error)
- AC5: 1 test (service)
- AC6: 1 test (model)
- AC7: 1 test (model)
- AC8: 3 tests (CLI integration)

**Total: 18 tests for 8 ACs** (>2 tests per AC on average)

---

## Summary Checklist

Before marking feature complete, verify:

### Spec Adherence
- [ ] All acceptance criteria have passing tests
- [ ] CLI contract matches spec exactly (arguments, options, output)
- [ ] Service contract matches spec exactly (signature, behavior)
- [ ] Model contract matches spec exactly (fields, validation, defaults)
- [ ] Error messages are user-friendly (match spec examples)

### Traceability
- [ ] All tests include spec references in docstrings
- [ ] All code includes spec references in docstrings
- [ ] Traceability matrix created and accurate
- [ ] AC tags used consistently

### Coverage
- [ ] Every AC has at least one test
- [ ] All edge cases from spec tested
- [ ] All error scenarios from spec tested
- [ ] Overall test coverage >90%

### Quality
- [ ] Type check passes (mypy --strict)
- [ ] Linter passes (ruff check)
- [ ] Formatter passes (ruff format --check)
- [ ] All tests pass (pytest)

### Documentation
- [ ] Docstrings reference spec sections
- [ ] Code comments explain "why" (spec requirement)
- [ ] README updated with new feature
- [ ] CHANGELOG updated
