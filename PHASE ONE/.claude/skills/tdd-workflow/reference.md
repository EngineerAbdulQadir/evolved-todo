# TDD Workflow Reference

## TDD History and Philosophy

Test-Driven Development was popularized by Kent Beck as part of Extreme Programming (XP) in the late 1990s. The core philosophy: **write tests first, then make them pass, then refactor**.

### The Three Laws of TDD (Uncle Bob Martin)

1. **You must write a failing test before you write any production code**
2. **You must not write more of a test than is sufficient to fail**
3. **You must not write more production code than is sufficient to pass the failing test**

## TDD Cycle Timing

Optimal cycle times for maximum productivity:

- **Red phase**: 1-3 minutes (write failing test)
- **Green phase**: 2-5 minutes (make test pass)
- **Refactor phase**: 3-8 minutes (improve code)
- **Total cycle**: 6-16 minutes per feature increment

If cycles take longer, break the task into smaller pieces.

## TDD Benefits

### Immediate Benefits
- Fewer bugs in production
- Better code design (testable = modular)
- Living documentation (tests show how code works)
- Confidence to refactor

### Long-term Benefits
- Lower maintenance costs
- Faster feature development (paradoxically)
- Better team collaboration
- Reduced debugging time

## Common TDD Mistakes

### Mistake 1: Writing Too Much Test Code

```python
# ❌ Bad: Testing implementation details
def test_add_task_implementation():
    service = TaskService(store, id_gen)
    assert service._store == store  # Testing internal state
    assert service._id_gen == id_gen
    task = service.add("Title")
    assert task in service._store._tasks.values()  # Testing internal structure
```

```python
# ✅ Good: Testing behavior
def test_add_task_creates_task():
    service = TaskService(store, id_gen)
    task = service.add("Title")
    retrieved = service.get(task.id)
    assert retrieved.title == "Title"
```

### Mistake 2: Skipping the Red Phase

Always verify tests fail before implementing:

```python
def test_new_feature():
    result = new_feature()
    assert result == "expected"

# MUST run this test and see it fail!
# If it passes immediately, something is wrong
```

### Mistake 3: Not Refactoring

```python
# After Green phase, you have duplication:
def add_task(self, title: str) -> Task:
    if not title or not title.strip():
        raise ValidationError("Title empty")
    if len(title) > 200:
        raise ValidationError("Title too long")
    # ...

def update_task(self, id: int, title: str) -> Task:
    if not title or not title.strip():
        raise ValidationError("Title empty")
    if len(title) > 200:
        raise ValidationError("Title too long")
    # ...

# REFACTOR: Extract validation
def _validate_title(self, title: str) -> None:
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")
    if len(title) > 200:
        raise ValidationError("Title cannot exceed 200 characters")
```

## TDD Patterns

### Pattern: Triangulation

When unsure of the generalization, use multiple test cases:

```python
def test_priority_ordering_low():
    assert priority_value(Priority.LOW) == 1

def test_priority_ordering_medium():
    assert priority_value(Priority.MEDIUM) == 2

def test_priority_ordering_high():
    assert priority_value(Priority.HIGH) == 3

# These three tests force you to implement proper ordering
```

### Pattern: Fake It Till You Make It

Start with simplest possible implementation:

```python
# Test
def test_get_next_id():
    gen = IdGenerator()
    assert gen.next() == 1

# Fake implementation
class IdGenerator:
    def next(self) -> int:
        return 1  # Just return 1!

# Add another test to force generalization
def test_get_sequential_ids():
    gen = IdGenerator()
    assert gen.next() == 1
    assert gen.next() == 2

# Now implement properly
class IdGenerator:
    def __init__(self) -> None:
        self._current = 0

    def next(self) -> int:
        self._current += 1
        return self._current
```

### Pattern: Obvious Implementation

For simple logic, skip faking:

```python
def test_task_completion_toggle():
    task = Task(id=1, title="Test")
    task.toggle_complete()
    assert task.is_complete

# Obvious implementation
class Task:
    def toggle_complete(self) -> None:
        self.is_complete = not self.is_complete
```

## TDD with Different Test Types

### Unit Tests (Fast, Isolated)
```python
# Test in milliseconds
def test_task_validation():
    with pytest.raises(ValidationError):
        Task(id=1, title="")
```

### Integration Tests (Slower, Multiple Components)
```python
# Test in tens of milliseconds
def test_add_command_integration():
    runner = CliRunner()
    result = runner.invoke(app, ["add", "Buy milk"])
    assert result.exit_code == 0
```

### End-to-End Tests (Slowest, Full System)
```python
# Test in hundreds of milliseconds
def test_full_task_lifecycle():
    # Add -> List -> Update -> Complete -> Delete
    pass
```

**TDD Rule**: Write mostly unit tests, some integration tests, few E2E tests (Test Pyramid)

## TDD Metrics

Track these metrics to improve:

- **Test Coverage**: Target >90% line coverage
- **Mutation Score**: How many test-detected bugs? (use mutmut)
- **Cycle Time**: How long per Red-Green-Refactor cycle?
- **Test/Code Ratio**: Typically 1:1 to 3:1 (test code : production code)

## Advanced TDD Techniques

### Outside-In TDD (London School)

Start with high-level tests, mock dependencies:

```python
# 1. Start with acceptance test
def test_add_command_creates_task():
    result = run_cli(["add", "Buy milk"])
    assert "created" in result.output

# 2. Drives creation of CLI command (mock service)
def test_add_command_calls_service(mock_service):
    add_command("Buy milk")
    mock_service.add.assert_called_once_with("Buy milk")

# 3. Then implement service with unit tests
def test_service_add_creates_task():
    task = service.add("Buy milk")
    assert task.title == "Buy milk"
```

### Inside-Out TDD (Chicago/Detroit School)

Start with domain models, build up:

```python
# 1. Start with model
def test_task_creation():
    task = Task(id=1, title="Buy milk")
    assert task.title == "Buy milk"

# 2. Build service using real models
def test_service_uses_task():
    task = service.add("Buy milk")
    assert isinstance(task, Task)

# 3. Build CLI using real service
def test_cli_uses_service():
    result = run_cli(["add", "Buy milk"])
    tasks = service.all()
    assert len(tasks) == 1
```

## TDD Anti-Patterns to Avoid

1. **The Liar**: Test passes but doesn't test what it claims
2. **Excessive Setup**: Test requires 50 lines of setup
3. **The Giant**: Test is 100+ lines long
4. **The Mockery**: Everything is mocked, nothing is real
5. **The Inspector**: Tests private methods instead of public API
6. **Success Against All Odds**: Test passes for wrong reason

## Resources

- Book: "Test Driven Development: By Example" - Kent Beck
- Book: "Growing Object-Oriented Software, Guided by Tests" - Freeman & Pryce
- Online: pytest documentation
- Tool: pytest-cov for coverage
- Tool: mutmut for mutation testing
