---
name: debugging
description: Systematic debugging strategies and tools. Use when tests fail, investigating bugs, understanding code behavior, or troubleshooting performance.
---

# Debugging

## Instructions

### When to Use

- When tests fail unexpectedly
- Investigating bug reports
- Understanding code behavior
- Performance issues

## Examples

### Debugging Strategies

### 1. Scientific Method

```
1. Reproduce: Create minimal test case
2. Hypothesize: Form theory about cause
3. Test: Add logging/breakpoints to verify
4. Fix: Implement solution
5. Verify: Confirm fix with tests
```

### 2. Binary Search

```python
# Narrow down problem location
# Comment out half the code, check if issue persists
# Repeat until you find the problematic section
```

### 3. Rubber Duck Debugging

Explain the problem out loud or in writing:
- What should happen?
- What actually happens?
- Where is the disconnect?

## Debugging Tools

### Print Debugging

```python
def complex_function(data: List[Task]) -> List[Task]:
    print(f"Input: {len(data)} tasks")  # Entry point

    filtered = [t for t in data if not t.is_complete]
    print(f"After filter: {len(filtered)} tasks")  # Checkpoint

    sorted_tasks = sorted(filtered, key=lambda t: t.priority)
    print(f"After sort: {len(sorted_tasks)} tasks")  # Exit point

    return sorted_tasks
```

### Python Debugger (pdb)

```python
import pdb

def problematic_function():
    x = calculate_something()
    pdb.set_trace()  # Execution pauses here
    # Now you can inspect variables interactively:
    # (Pdb) print(x)
    # (Pdb) type(x)
    # (Pdb) next  # Execute next line
    # (Pdb) continue  # Resume execution
    return x * 2
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def risky_operation(task_id: int) -> Task:
    logger.debug(f"Fetching task {task_id}")
    task = store.get(task_id)

    if not task:
        logger.warning(f"Task {task_id} not found")
        raise TaskNotFoundError(f"Task #{task_id} not found")

    logger.debug(f"Found task: {task.title}")
    return task
```

### Pytest Debugging

```bash
# Run with verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Run specific test
uv run pytest tests/unit/test_models.py::test_validation -v

# Drop into pdb on failure
uv run pytest --pdb
```

## Common Bug Patterns

### Off-by-One Errors

```python
# ❌ Common mistake
for i in range(len(tasks)):
    if i < len(tasks) - 1:  # Missing last item
        process(tasks[i])

# ✅ Correct
for task in tasks:
    process(task)
```

### Mutable Default Arguments

```python
# ❌ Bug: list is shared across calls
def add_tags(task: Task, tags: List[str] = []) -> None:
    tags.append("new-tag")
    task.tags = tags

# ✅ Fix: use None as default
def add_tags(task: Task, tags: Optional[List[str]] = None) -> None:
    if tags is None:
        tags = []
    tags.append("new-tag")
    task.tags = tags
```

### None Handling

```python
# ❌ Crashes on None
def process_task(task: Optional[Task]) -> str:
    return task.title  # AttributeError if task is None

# ✅ Check for None
def process_task(task: Optional[Task]) -> str:
    if task is None:
        return "No task"
    return task.title
```

## Debugging Checklist

When encountering a bug:

- [ ] Can you reproduce it consistently?
- [ ] What's the minimal test case?
- [ ] What changed recently?
- [ ] Do tests cover this scenario?
- [ ] What do the logs say?
- [ ] Did you check variable types?
- [ ] Are there any None values?
- [ ] Is it an off-by-one error?
- [ ] Did you read the error message carefully?

## Prevention

Best debugging is preventing bugs:

- Write tests first (TDD)
- Use type hints (mypy)
- Enable strict linting (ruff)
- Code review
- Add assertions for invariants
