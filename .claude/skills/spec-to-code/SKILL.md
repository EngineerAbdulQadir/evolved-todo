---
name: spec-to-code
description: Convert specification documents and tasks into implementation following SDD principles. Use when starting implementation of any user story phase from tasks.md.
---

# Spec-to-Code

## Instructions

### When to Use

Use this skill when:
- Starting implementation of any user story phase (Phase 3-12) from tasks.md
- Converting acceptance criteria to test stubs
- Ensuring spec-to-code traceability
- Verifying all ACs are covered by tests
- Generating implementation checklists

### Core Workflow (SDD Methodology)

### Step 1: Read Specification

Before implementing any task, read the relevant spec:

```bash
# Example for US1 (Add Task)
specs/001-phase1-todo-app/001-add-task/spec.md
```

Extract:
- **User Story**: What the user wants to achieve
- **Acceptance Criteria**: Testable requirements
- **Technical Details**: Models, services, CLI commands
- **Edge Cases**: Error conditions, validations

### Step 2: Map Spec to Tasks

Cross-reference spec with task list:

```bash
# From tasks.md
## Phase 3: US1 - Add Task (P1)
- [ ] T019 [US1] Write unit tests for TaskService.add()
- [ ] T020 [US1] Implement TaskService.add() with validation
- [ ] T021 [US1] Write unit tests for Task validation
- [ ] T022 [US1] Implement Task title validation
...
```

### Step 3: Implementation Order

Follow dependency order:
1. **Models first** (data structures + validation)
2. **Services second** (business logic)
3. **CLI last** (user interface)

### Step 4: Code Generation Template

For each task, generate code following this template:

#### Model Implementation

```python
# From spec: "Tasks must have a title (required, 1-200 chars)"
# Task: T022 - Implement Task title validation

@dataclass
class Task:
    title: str

    def __post_init__(self) -> None:
        self._validate_title()

    def _validate_title(self) -> None:
        """Title: 1-200 chars, non-empty (Spec: 001-add-task section 2.1)."""
        if not self.title or not self.title.strip():
            raise ValidationError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValidationError("Title cannot exceed 200 characters")
```

#### Service Implementation

```python
# From spec: "System shall generate sequential integer IDs"
# Task: T020 - Implement TaskService.add()

class TaskService:
    def add(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task (Spec: 001-add-task section 3.1).

        Args:
            title: Task title (1-200 chars)
            description: Optional description (max 1000 chars)

        Returns:
            Created task with generated ID

        Raises:
            ValidationError: If title/description invalid
        """
        task = Task(
            id=self._id_gen.next(),
            title=title,
            description=description,
        )
        # Task validates itself in __post_init__
        self._store.save(task)
        return task
```

#### CLI Implementation

```python
# From spec: "CLI command: todo add <title> [--desc <text>]"
# Task: T024 - Create CLI add command

@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title (1-200 chars)"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Task description (max 1000 chars)"),
) -> None:
    """
    Create a new task (Spec: 001-add-task section 4.1).

    Examples:
        todo add "Buy milk"
        todo add "Buy milk" --desc "From store on Main St"
    """
    try:
        task = task_service.add(title=title, description=desc)
        console.print(f"[green]✓[/green] Task #{task.id} created: {task.title}")
    except ValidationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
```

## Spec Traceability

Always include spec references in:
- **Docstrings**: `(Spec: 001-add-task section 3.1)`
- **Comments**: `# From spec: "Sequential integer IDs"`
- **Test names**: `test_add_task_validates_title_per_spec`

## Acceptance Criteria Mapping

For each acceptance criterion in the spec, create at least one test:

```python
# Spec acceptance criteria:
# - AC1: User can create task with just title
# - AC2: User can optionally add description
# - AC3: Title must be 1-200 chars
# - AC4: Description max 1000 chars
# - AC5: System generates unique ID

# Tests:
def test_create_task_with_title_only():  # AC1
    """User can create task with just title."""
    task = task_service.add(title="Buy milk")
    assert task.title == "Buy milk"
    assert task.description is None

def test_create_task_with_description():  # AC2
    """User can optionally add description."""
    task = task_service.add(title="Buy milk", description="From store")
    assert task.description == "From store"

def test_title_validation_min_length():  # AC3
    """Title must be at least 1 char."""
    with pytest.raises(ValidationError):
        task_service.add(title="")

def test_title_validation_max_length():  # AC3
    """Title cannot exceed 200 chars."""
    with pytest.raises(ValidationError):
        task_service.add(title="x" * 201)

def test_description_max_length():  # AC4
    """Description cannot exceed 1000 chars."""
    with pytest.raises(ValidationError):
        task_service.add(title="Valid", description="x" * 1001)

def test_sequential_id_generation():  # AC5
    """System generates unique sequential IDs."""
    task1 = task_service.add(title="Task 1")
    task2 = task_service.add(title="Task 2")
    assert task2.id == task1.id + 1
```

## Examples

### Example: Full US1 Implementation Flow

### 1. Read Spec
```bash
specs/001-phase1-todo-app/001-add-task/spec.md
```

### 2. Extract Requirements
- User story: Create tasks with title + optional description
- Models: Task dataclass with validation
- Service: TaskService.add() method
- CLI: `todo add <title> [--desc <text>]`
- Acceptance: 5 criteria (see above)

### 3. Implement in Order
1. T021-T023: Task model + validation (with tests)
2. T019-T020: TaskService.add() (with tests)
3. T024-T026: CLI command + formatter (with tests)
4. T025: Integration tests

### 4. Verify Against Spec
- [ ] All acceptance criteria have tests
- [ ] All spec requirements implemented
- [ ] CLI matches contract in `contracts/cli-commands.md`
- [ ] Error messages user-friendly

### Helper Scripts

Use the automation scripts to streamline spec-to-code conversion:

#### Generate Test Stubs from Spec
```bash
python .claude/skills/spec-to-code/scripts/helper.py generate-tests \
  --spec specs/001-phase1-todo-app/001-add-task/spec.md \
  --output tests/unit/test_add_task.py
```

#### Verify AC Coverage
```bash
python .claude/skills/spec-to-code/scripts/helper.py verify-coverage \
  --spec specs/001-phase1-todo-app/001-add-task/spec.md \
  --tests tests/
```

#### Generate Implementation Checklist
```bash
python .claude/skills/spec-to-code/scripts/helper.py generate-checklist \
  --spec specs/001-phase1-todo-app/001-add-task/spec.md
```

#### Create Traceability Matrix
```bash
python .claude/skills/spec-to-code/scripts/helper.py create-matrix \
  --spec specs/001-phase1-todo-app/001-add-task/spec.md \
  --tests tests/ \
  --code src/
```

### Templates Available

Located in `.claude/skills/spec-to-code/templates/`:
- **Test templates** - Unit and integration test stubs with AC references
- **Model templates** - Dataclass implementation with validation
- **Service templates** - Business logic with dependency injection
- **CLI templates** - Typer commands with Rich formatting
- **Checklist templates** - Implementation tracking
- **Matrix templates** - Traceability documentation

## Integration with Other Skills

- **tdd-workflow**: Follow Red-Green-Refactor for each task
- **model-service**: Use patterns for implementation
- **cli-command**: Follow CLI standards
- **testing-patterns**: Create comprehensive tests

## Integration with Subagents

After implementation, invoke these subagents for verification:
- **constitution-compliance**: Verify implementation follows project principles
- **doc-curator**: Ensure spec references in code/docstrings
- **test-guardian**: Verify all acceptance criteria tested
- **type-enforcer**: Validate type annotations match contracts
- **security-sentinel**: Review input validation against spec requirements

## Key Success Metrics

Spec-to-code implementation is successful when:
1. ✅ Every AC has at least one passing test
2. ✅ All technical contracts match spec exactly
3. ✅ Traceability comments link code to spec
4. ✅ Test coverage >90% for feature code
5. ✅ All quality gates pass (mypy, ruff, pytest)
6. ✅ Helper script `verify-coverage` passes with 100%

## See Also

- **reference.md**: Comprehensive SDD methodology guide, AC patterns, traceability techniques
- **examples.md**: Complete implementation examples (US1, US2, US5, multi-phase features)
- **scripts/helper.py**: Automation tools for test generation, coverage verification, matrix creation
- **templates/**: Ready-to-use templates for tests, models, services, CLI, checklists
