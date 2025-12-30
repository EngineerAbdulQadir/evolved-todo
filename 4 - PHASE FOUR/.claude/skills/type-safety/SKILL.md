---
name: type-safety
description: Ensure comprehensive type annotations and mypy strict mode compliance. Use when writing new functions, after implementing features, or before committing code.
---

# Type Safety

## Instructions

### When to Use

- Writing any new function, class, or method
- After implementing new features
- Before committing code
- When mypy reports type errors

## Examples

### Type Annotation Patterns

### 1. Function Signatures

```python
from typing import Optional, List, Dict, Set, Any
from datetime import datetime, date

# All parameters and return types annotated
def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    tags: Optional[Set[str]] = None,
) -> Task:
    """Create new task with validation."""
    ...

# Void functions return None
def delete_task(task_id: int) -> None:
    """Delete task by ID."""
    ...

# Functions that may return None
def find_task(title: str) -> Optional[Task]:
    """Find task by title, return None if not found."""
    ...
```

### 2. Class Attributes

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class Task:
    # Required attributes
    id: int
    title: str

    # Optional attributes with defaults
    description: Optional[str] = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    # Collections with defaults
    tags: Set[str] = field(default_factory=set)

    # Class variables
    MAX_TITLE_LENGTH: ClassVar[int] = 200
```

### 3. Collections

```python
from typing import List, Dict, Set, Tuple

# Specific types, not just list/dict
tasks: List[Task] = []
task_map: Dict[int, Task] = {}
unique_tags: Set[str] = set()
coordinates: Tuple[int, int] = (0, 0)

# Nested collections
tasks_by_priority: Dict[Priority, List[Task]] = {}
```

### 4. Union Types

```python
from typing import Union

# Union for multiple possible types
def process_input(value: Union[str, int]) -> str:
    """Process string or integer input."""
    return str(value)

# Modern Python 3.10+ syntax
def process_input(value: str | int) -> str:
    """Process string or integer input."""
    return str(value)
```

### 5. Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Repository(Generic[T]):
    """Generic repository pattern."""

    def __init__(self) -> None:
        self._items: Dict[int, T] = {}

    def add(self, item: T) -> None:
        """Add item to repository."""
        ...

    def get(self, id: int) -> Optional[T]:
        """Get item by ID."""
        return self._items.get(id)

    def all(self) -> List[T]:
        """Get all items."""
        return list(self._items.values())
```

### 6. Callable Types

```python
from typing import Callable

# Function that takes a function as parameter
def apply_to_tasks(
    func: Callable[[Task], bool],
    tasks: List[Task]
) -> List[Task]:
    """Filter tasks using provided function."""
    return [t for t in tasks if func(t)]

# With specific signature
Validator = Callable[[str], bool]

def validate_input(value: str, validator: Validator) -> bool:
    """Validate input using validator function."""
    return validator(value)
```

## Mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
check_untyped_defs = true
```

## Common Mypy Errors and Fixes

### Error: Missing return type

```python
# ❌ Error
def calculate(x: int):
    return x * 2

# ✅ Fixed
def calculate(x: int) -> int:
    return x * 2
```

### Error: Implicit Optional

```python
# ❌ Error
def process(value: str = None):
    ...

# ✅ Fixed
def process(value: Optional[str] = None) -> None:
    ...
```

### Error: Untyped self/cls

```python
# ❌ Error
class Task:
    def __init__(self, id, title):
        self.id = id
        self.title = title

# ✅ Fixed
class Task:
    def __init__(self, id: int, title: str) -> None:
        self.id: int = id
        self.title: str = title
```

### Error: Incompatible types in assignment

```python
# ❌ Error
def get_task(id: int) -> Task:
    task = store.get(id)  # Returns Optional[Task]
    return task  # Error: might be None

# ✅ Fixed
def get_task(id: int) -> Task:
    task = store.get(id)
    if task is None:
        raise TaskNotFoundError(f"Task #{id} not found")
    return task  # Now guaranteed to be Task
```

## Type Narrowing

```python
from typing import Union

def process_value(value: Union[str, int, None]) -> str:
    """Type narrowing with if statements."""
    if value is None:
        return "empty"

    # After None check, value is Union[str, int]
    if isinstance(value, str):
        return value.upper()

    # After str check, value is int
    return str(value * 2)
```

## Protocol Types (Structural Subtyping)

```python
from typing import Protocol

class Storable(Protocol):
    """Protocol for objects that can be stored."""
    id: int
    created_at: datetime

    def validate(self) -> None:
        """Validate object."""
        ...

def save_to_store(item: Storable) -> None:
    """Save any object that implements Storable protocol."""
    item.validate()
    store.save(item)
```

## Type Guards

```python
from typing import TypeGuard

def is_task_list(value: object) -> TypeGuard[List[Task]]:
    """Type guard to check if value is List[Task]."""
    return (
        isinstance(value, list) and
        all(isinstance(item, Task) for item in value)
    )

def process(data: object) -> None:
    """Process data if it's a task list."""
    if is_task_list(data):
        # data is now narrowed to List[Task]
        for task in data:
            print(task.title)
```

## Literal Types

```python
from typing import Literal

SortField = Literal["id", "title", "priority", "due_date"]
SortOrder = Literal["asc", "desc"]

def sort_tasks(
    tasks: List[Task],
    field: SortField,
    order: SortOrder = "asc"
) -> List[Task]:
    """Sort tasks by field and order."""
    ...
```

## Type Aliases

```python
from typing import TypeAlias

# Simple aliases
TaskID: TypeAlias = int
TagSet: TypeAlias = Set[str]

# Complex aliases
TaskFilter: TypeAlias = Callable[[Task], bool]
TaskDict: TypeAlias = Dict[int, Task]
```

## Running Type Checks

```bash
# Check all source files
uv run mypy --strict src/

# Check specific file
uv run mypy --strict src/services/task_service.py

# Show error context
uv run mypy --strict --show-error-context src/

# Generate coverage report
uv run mypy --strict --html-report mypy-report src/
```

## Type Checking in Tests

```python
# tests/unit/test_types.py
from typing import reveal_type

def test_type_inference():
    """Test that mypy correctly infers types."""
    task = Task(id=1, title="Test")

    # Use reveal_type for debugging (mypy will show the inferred type)
    reveal_type(task)  # Revealed type is 'Task'
    reveal_type(task.id)  # Revealed type is 'int'
```

## Integration with type-enforcer Subagent

Invoke after implementation:

```
Reviews:
- All public APIs have type annotations
- No Any types without justification
- Proper use of Optional vs Union
- Type narrowing for conditional branches
- Generic types used correctly
- mypy --strict passes without errors
```

## See Also

- `reference.md` - Advanced typing patterns
- `templates/typed-class-template.py` - Type-safe class template
- `scripts/type-coverage.py` - Calculate type annotation coverage
