# Testing Patterns - Extended Reference

## Table of Contents

1. [Pytest Fundamentals](#pytest-fundamentals)
2. [Test Structure (AAA Pattern)](#test-structure-aaa-pattern)
3. [Fixtures Deep Dive](#fixtures-deep-dive)
4. [Parametrized Testing](#parametrized-testing)
5. [Mocking and Doubles](#mocking-and-doubles)
6. [Exception Testing](#exception-testing)
7. [CLI Testing with Typer](#cli-testing-with-typer)
8. [Coverage Analysis](#coverage-analysis)
9. [Common Mistakes](#common-mistakes)
10. [Best Practices](#best-practices)

---

## Pytest Fundamentals

### Why Pytest?

Pytest is the modern Python testing framework:
- Simple, Pythonic syntax (no class/method boilerplate required)
- Powerful fixtures for setup/teardown
- Excellent failure reporting
- Built-in discovery (finds tests automatically)
- Rich plugin ecosystem
- Parametrized testing built-in

### Test Discovery

Pytest automatically finds tests matching these patterns:
- Files: `test_*.py` or `*_test.py`
- Functions: `test_*`
- Classes: `Test*`
- Methods: `test_*`

```python
# tests/unit/test_task.py -  Discovered
# tests/task_test.py -  Discovered
# tests/my_task.py - L NOT discovered

def test_something():  #  Discovered
    pass

def something_test():  # L NOT discovered
    pass

class TestTask:  #  Discovered
    def test_method(self):  #  Discovered
        pass
```

### Assertions

Pytest enhances standard Python assertions with detailed failure messages:

```python
def test_task_title():
    task = Task(id=1, title="Test")

    # Simple assertion
    assert task.title == "Test"

    # Multiple assertions (best practice: one assertion per test)
    assert task.id == 1
    assert task.title == "Test"
    assert not task.is_complete

# When test fails, pytest shows:
# AssertionError: assert 'Test' == 'Tes'
#   - Tes
#   ?    ^
#   + Test
#   ?    +
```

---

## Test Structure (AAA Pattern)

### Arrange-Act-Assert

Every test should follow the AAA pattern:

```python
def test_add_task():
    # Arrange: Set up test data and dependencies
    service = TaskService(store=InMemoryStore(), id_gen=IdGen())
    title = "Buy groceries"

    # Act: Execute the code being tested
    result = service.add(title=title)

    # Assert: Verify expected behavior
    assert result.id == 1
    assert result.title == title
```

### Given-When-Then (BDD Style)

Alternative naming convention (same pattern):

```python
def test_task_becomes_complete_when_toggled():
    # Given: A task exists
    task = Task(id=1, title="Test", is_complete=False)

    # When: Toggle is called
    task.is_complete = not task.is_complete

    # Then: Task is complete
    assert task.is_complete
```

---

## Fixtures Deep Dive

### What are Fixtures?

Fixtures provide reusable setup for tests:
- Clean test data
- Configured services
- Mock objects
- Test resources (files, db connections)

### Basic Fixture

```python
import pytest
from src.services.task_service import TaskService

@pytest.fixture
def task_service():
    """Create fresh TaskService for each test."""
    return TaskService(
        store=InMemoryStore(),
        id_gen=SequentialIdGen()
    )

def test_add_task(task_service):
    """Pytest automatically calls fixture and injects result."""
    task = task_service.add(title="Test")
    assert task.id == 1
```

### Fixture Scopes

Control fixture lifetime with `scope` parameter:

```python
# Function scope (default) - runs before EACH test
@pytest.fixture(scope="function")
def fresh_service():
    return TaskService()

# Class scope - runs once per test class
@pytest.fixture(scope="class")
def shared_service():
    return TaskService()

# Module scope - runs once per test file
@pytest.fixture(scope="module")
def module_service():
    return TaskService()

# Session scope - runs once for entire test session
@pytest.fixture(scope="session")
def database():
    db = Database()
    yield db
    db.close()  # Cleanup after all tests
```

### Fixture Dependencies

Fixtures can use other fixtures:

```python
@pytest.fixture
def task_store():
    """In-memory store."""
    return InMemoryStore()

@pytest.fixture
def id_gen():
    """ID generator."""
    return SequentialIdGen()

@pytest.fixture
def task_service(task_store, id_gen):
    """Service using other fixtures."""
    return TaskService(store=task_store, id_gen=id_gen)

def test_something(task_service):
    """Gets fully configured service."""
    pass
```

### Autouse Fixtures

Fixtures that run automatically without being requested:

```python
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset global state before each test."""
    GlobalConfig.reset()
    yield
    GlobalConfig.reset()  # Cleanup
```

### Fixture Factories

Fixtures can return factory functions for flexibility:

```python
@pytest.fixture
def make_task():
    """Factory to create custom tasks."""
    def _make(title="Test", **kwargs):
        return Task(id=1, title=title, **kwargs)
    return _make

def test_with_factory(make_task):
    task1 = make_task(title="First")
    task2 = make_task(title="Second", priority=Priority.HIGH)

    assert task1.title != task2.title
```

---

## Parametrized Testing

### Basic Parametrization

Test same logic with multiple inputs:

```python
@pytest.mark.parametrize("title,expected_valid", [
    ("Valid title", True),
    ("x" * 200, True),  # Exactly max length
    ("x" * 201, False),  # Exceeds max
    ("", False),  # Empty
    ("   ", False),  # Whitespace only
])
def test_title_validation(title, expected_valid):
    if expected_valid:
        task = Task(id=1, title=title)
        assert task.title == title
    else:
        with pytest.raises(ValidationError):
            Task(id=1, title=title)
```

### Multiple Parameters

```python
@pytest.mark.parametrize("priority,expected", [
    (Priority.LOW, "low"),
    (Priority.MEDIUM, "medium"),
    (Priority.HIGH, "high"),
])
def test_priority_values(priority, expected):
    assert priority.value == expected
```

### Parametrize Fixtures

```python
@pytest.fixture(params=[Priority.LOW, Priority.MEDIUM, Priority.HIGH])
def priority(request):
    """Test with all priority levels."""
    return request.param

def test_task_with_all_priorities(priority):
    """Runs 3 times, once for each priority."""
    task = Task(id=1, title="Test", priority=priority)
    assert task.priority == priority
```

### Named Parameters (IDs)

Add readable test names:

```python
@pytest.mark.parametrize("tag,should_pass", [
    pytest.param("valid-tag", True, id="hyphen_allowed"),
    pytest.param("valid_tag", True, id="underscore_allowed"),
    pytest.param("tag@special", False, id="special_char_rejected"),
])
def test_tag_validation(tag, should_pass):
    if should_pass:
        Task(id=1, title="Test", tags={tag})
    else:
        with pytest.raises(ValidationError):
            Task(id=1, title="Test", tags={tag})
```

---

## Mocking and Doubles

### unittest.mock

Python's built-in mocking library:

```python
from unittest.mock import Mock, patch

def test_service_calls_store():
    """Verify service calls store.save()."""
    # Create mock store
    mock_store = Mock()
    service = TaskService(store=mock_store, id_gen=IdGen())

    # Execute
    task = service.add(title="Test")

    # Verify interactions
    mock_store.save.assert_called_once()
    assert mock_store.save.call_args[0][0].title == "Test"
```

### Mock Return Values

```python
def test_get_calls_store():
    mock_store = Mock()
    expected_task = Task(id=1, title="Test")

    # Configure mock to return specific value
    mock_store.get.return_value = expected_task

    service = TaskService(store=mock_store, id_gen=IdGen())
    result = service.get(1)

    assert result == expected_task
    mock_store.get.assert_called_once_with(1)
```

### Mock Side Effects

```python
def test_retries_on_failure():
    mock_store = Mock()

    # First call fails, second succeeds
    mock_store.save.side_effect = [
        StorageError("Connection failed"),
        None  # Success
    ]

    service = TaskService(store=mock_store, id_gen=IdGen())

    # Should retry and succeed
    task = service.add_with_retry(title="Test")

    assert mock_store.save.call_count == 2
```

### Patch Decorator

Replace functions/objects temporarily:

```python
from datetime import datetime

@patch('src.models.task.datetime')
def test_task_created_at(mock_datetime):
    """Mock datetime.now() for consistent tests."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time

    task = Task(id=1, title="Test")

    assert task.created_at == fixed_time
```

---

## Exception Testing

### Basic Exception Testing

```python
import pytest
from src.models.exceptions import ValidationError

def test_empty_title_raises_error():
    """Verify specific exception is raised."""
    with pytest.raises(ValidationError):
        Task(id=1, title="")
```

### Exception Message Matching

```python
def test_exception_message():
    """Verify exception message contains text."""
    with pytest.raises(ValidationError, match="cannot be empty"):
        Task(id=1, title="")

    # Regex matching
    with pytest.raises(ValidationError, match=r"exceeds \d+ characters"):
        Task(id=1, title="x" * 201)
```

### Inspecting Exception

```python
def test_exception_attributes():
    """Access exception object for detailed assertions."""
    with pytest.raises(ValidationError) as exc_info:
        Task(id=1, title="")

    # Access exception
    exception = exc_info.value

    assert "empty" in str(exception)
    assert exception.args[0] == "Title cannot be empty"
```

---

## CLI Testing with Typer

### CliRunner Basics

```python
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_add_command():
    """Test CLI command invocation."""
    result = runner.invoke(app, ["add", "Buy milk"])

    assert result.exit_code == 0
    assert "created" in result.stdout.lower()
```

### Testing Command Options

```python
def test_add_with_options():
    """Test CLI with multiple options."""
    result = runner.invoke(app, [
        "add",
        "Important task",
        "--desc", "Very important",
        "--priority", "high",
        "--tags", "work,urgent"
    ])

    assert result.exit_code == 0
    assert "Important task" in result.stdout
```

### Testing Interactive Prompts

```python
def test_delete_confirmation():
    """Test interactive confirmation prompt."""
    result = runner.invoke(
        app,
        ["delete", "1"],
        input="y\n"  # Simulate typing 'y' and Enter
    )

    assert result.exit_code == 0
    assert "deleted" in result.stdout.lower()
```

### Testing Error Exit Codes

```python
def test_invalid_input_returns_error_code():
    """Verify non-zero exit code on error."""
    result = runner.invoke(app, ["add", ""])

    assert result.exit_code != 0  # Should fail
    assert "error" in result.stdout.lower()
```

---

## Coverage Analysis

### Running with Coverage

```bash
# Basic coverage
uv run pytest --cov=src

# With missing lines report
uv run pytest --cov=src --cov-report=term-missing

# HTML report
uv run pytest --cov=src --cov-report=html

# Fail if below threshold
uv run pytest --cov=src --cov-fail-under=90
```

### Coverage Report Output

```
----------- coverage: platform win32, python 3.13.1 -----------
Name                      Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/__init__.py               0      0   100%
src/models/__init__.py        0      0   100%
src/models/task.py           45      2    96%   67-68
src/services/task_service.py 32      1    97%   45
--------------------------------------------------------
TOTAL                        77      3    96%
```

### Targeting Missing Lines

```python
# Line 67-68 not covered
def _validate_tags(self) -> None:
    for tag in self.tags:
        if len(tag) > 20:  # Line 67 - not tested!
            raise ValidationError(f"Tag '{tag}' exceeds 20 characters")
```

Add test to cover:

```python
def test_tag_exceeds_max_length():
    """Test tag validation for length."""
    long_tag = "x" * 21
    with pytest.raises(ValidationError, match="exceeds 20 characters"):
        Task(id=1, title="Test", tags={long_tag})
```

---

## Common Mistakes

### L Mistake 1: Multiple Assertions Without Clear Failure

```python
# L BAD - If first assertion fails, you don't know about others
def test_task_properties():
    task = Task(id=1, title="Test")
    assert task.id == 1
    assert task.title == "Test"
    assert not task.is_complete
```

```python
#  GOOD - Separate tests for each property
def test_task_id():
    task = Task(id=1, title="Test")
    assert task.id == 1

def test_task_title():
    task = Task(id=1, title="Test")
    assert task.title == "Test"

def test_task_defaults_to_incomplete():
    task = Task(id=1, title="Test")
    assert not task.is_complete
```

### L Mistake 2: Testing Implementation Instead of Behavior

```python
# L BAD - Tests internal implementation
def test_service_stores_in_dict():
    service = TaskService()
    task = service.add(title="Test")
    assert task.id in service._store._tasks  # Accessing internals!
```

```python
#  GOOD - Tests public behavior
def test_service_retrieves_added_task():
    service = TaskService()
    added = service.add(title="Test")
    retrieved = service.get(added.id)
    assert retrieved.title == "Test"
```

### L Mistake 3: Shared Mutable State

```python
# L BAD - Tasks list shared across tests
TASKS = []

def test_add_task():
    TASKS.append(Task(id=1, title="Test"))
    assert len(TASKS) == 1  # Fails if run after test_add_another!

def test_add_another():
    TASKS.append(Task(id=2, title="Test 2"))
    assert len(TASKS) == 1  # Assumes empty list!
```

```python
#  GOOD - Use fixtures for clean state
@pytest.fixture
def tasks():
    return []

def test_add_task(tasks):
    tasks.append(Task(id=1, title="Test"))
    assert len(tasks) == 1

def test_add_another(tasks):
    tasks.append(Task(id=2, title="Test 2"))
    assert len(tasks) == 1  # Fresh list each time
```

---

## Best Practices

### 1. One Assertion Per Test

Focus each test on a single behavior:

```python
#  GOOD
def test_add_generates_id():
    service = TaskService()
    task = service.add(title="Test")
    assert task.id == 1

def test_add_sets_title():
    service = TaskService()
    task = service.add(title="Test")
    assert task.title == "Test"
```

### 2. Test Names Describe Behavior

```python
# L BAD - Vague name
def test_task():
    pass

#  GOOD - Describes what is being tested
def test_task_title_cannot_exceed_200_characters():
    pass
```

### 3. Use Fixtures for Shared Setup

```python
#  GOOD - Reusable, clean
@pytest.fixture
def configured_service():
    return TaskService(store=InMemoryStore(), id_gen=IdGen())

def test_add(configured_service):
    task = configured_service.add(title="Test")
    assert task.id == 1
```

### 4. Test Edge Cases

Always test boundaries:

```python
def test_title_exactly_max_length():
    """Boundary test: exactly 200 chars."""
    title = "x" * 200
    task = Task(id=1, title=title)
    assert len(task.title) == 200

def test_title_exceeds_max_length():
    """Boundary test: 201 chars."""
    title = "x" * 201
    with pytest.raises(ValidationError):
        Task(id=1, title=title)
```

### 5. Test Error Paths

```python
def test_get_nonexistent_task_raises():
    """Error path: task doesn't exist."""
    service = TaskService()
    with pytest.raises(TaskNotFoundError):
        service.get(999)
```

### 6. Use Descriptive Variable Names

```python
#  GOOD
def test_update_changes_title():
    service = TaskService()
    original_task = service.add(title="Original")
    updated_task = service.update(original_task.id, title="Updated")

    assert updated_task.title == "Updated"
    assert original_task.id == updated_task.id
```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Effective Python Testing](https://realpython.com/pytest-python-testing/)
- [Python Testing with pytest (Book)](https://pragprog.com/titles/bopytest/)
- [Test-Driven Development](https://www.obeythetestinggoat.com/)
