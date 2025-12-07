---
name: refactoring
description: Improve code quality while preserving behavior. Use after implementing features, during code review, or weekly quality reviews.
---

# Refactoring

## Instructions

### When to Use

- After implementing features (refactor phase of TDD)
- During code review
- Weekly code quality reviews
- When code smells detected

## Examples

### Common Refactoring Patterns

### 1. Extract Method

```python
# ❌ Before: Long method
def add_task(self, title: str, **kwargs) -> Task:
    if not title or not title.strip():
        raise ValidationError("Title empty")
    if len(title) > 200:
        raise ValidationError("Title too long")

    desc = kwargs.get('description')
    if desc and len(desc) > 1000:
        raise ValidationError("Description too long")

    task = Task(id=self._id_gen.next(), title=title, **kwargs)
    self._store.save(task)
    return task

# ✅ After: Extracted validation
def add_task(self, title: str, **kwargs) -> Task:
    self._validate_title(title)
    self._validate_description(kwargs.get('description'))

    task = Task(id=self._id_gen.next(), title=title, **kwargs)
    self._store.save(task)
    return task

def _validate_title(self, title: str) -> None:
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")
    if len(title) > 200:
        raise ValidationError("Title cannot exceed 200 characters")

def _validate_description(self, desc: Optional[str]) -> None:
    if desc and len(desc) > 1000:
        raise ValidationError("Description cannot exceed 1000 characters")
```

### 2. Replace Magic Numbers with Constants

```python
# ❌ Magic numbers
if len(title) > 200:
    raise ValidationError("Title too long")

# ✅ Named constants
MAX_TITLE_LENGTH = 200

if len(title) > MAX_TITLE_LENGTH:
    raise ValidationError(
        f"Title cannot exceed {MAX_TITLE_LENGTH} characters"
    )
```

### 3. Simplify Conditionals

```python
# ❌ Complex nested conditions
if task:
    if task.is_complete:
        if task.priority == Priority.HIGH:
            return True
    return False

# ✅ Simplified with early returns
if not task:
    return False

if not task.is_complete:
    return False

return task.priority == Priority.HIGH
```

## Code Smells to Fix

- Long methods (>30 lines)
- Duplicate code
- Large classes (>300 lines)
- Long parameter lists (>5 params)
- Magic numbers/strings
- Deep nesting (>3 levels)

## Integration with refactoring-scout Subagent

Invoke weekly or before major releases:

```
Reviews:
- Identifies code duplication
- Suggests design pattern improvements
- Detects code smells
- Recommends refactoring priorities
```
