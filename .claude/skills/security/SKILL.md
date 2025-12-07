---
name: security
description: Implement secure coding practices and input validation. Use when processing user input, parsing external data, or implementing authentication.
---

# Security

## Instructions

### When to Use

- Processing user input
- Parsing external data (files, network)
- Implementing authentication/authorization
- Before committing code with user input handling

## Examples

### Input Validation Patterns

### 1. Whitelist Validation (Preferred)

```python
from enum import Enum

class Priority(Enum):
    """Whitelist of valid priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

def set_priority(value: str) -> Priority:
    """Validate priority using whitelist."""
    try:
        return Priority(value.lower())
    except ValueError:
        valid = ", ".join(p.value for p in Priority)
        raise ValidationError(
            f"Invalid priority '{value}'. Must be one of: {valid}"
        )
```

### 2. Length Validation

```python
def validate_title(title: str) -> None:
    """Validate title length and content."""
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    if len(title) > 200:
        raise ValidationError(
            f"Title too long ({len(title)} > 200 chars)"
        )
```

### 3. Pattern Validation (Regex)

```python
import re

def validate_tag(tag: str) -> None:
    """Validate tag format: alphanumeric, hyphens, underscores only."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
        raise ValidationError(
            f"Tag '{tag}' contains invalid characters. "
            f"Use only letters, numbers, hyphens, and underscores."
        )

    if len(tag) > 20:
        raise ValidationError(f"Tag '{tag}' exceeds 20 characters")
```

## OWASP Top 10 Prevention

### 1. Injection Prevention

```python
# ✅ Safe: No string interpolation in queries
# (Not applicable for in-memory storage, but important for future DB)

# If using SQL in future:
# cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
```

### 2. Sanitize Output

```python
from rich.console import Console

console = Console()

def display_task(task: Task) -> None:
    """Display task safely (rich handles escaping)."""
    # Rich automatically escapes special characters
    console.print(f"Title: {task.title}")
    console.print(f"Description: {task.description}")
```

### 3. No Secrets in Code

```python
# ❌ Never do this
API_KEY = "sk-1234567890abcdef"

# ✅ Use environment variables
import os
API_KEY = os.getenv("TODO_API_KEY")
if not API_KEY:
    raise RuntimeError("TODO_API_KEY environment variable not set")
```

### 4. Secure Error Messages

```python
# ❌ Too much information
except Exception as e:
    console.print(f"Error: {traceback.format_exc()}")

# ✅ User-friendly, not revealing internals
except TaskNotFoundError as e:
    console.print(f"[red]Error:[/red] {e}")
except Exception:
    console.print("[red]An unexpected error occurred[/red]")
    logger.exception("Unexpected error")  # Log details server-side
```

## Integration with security-sentinel Subagent

Invoke before committing:

```
Reviews:
- Input validation completeness
- No command injection vectors
- No information leakage in errors
- Secrets handled securely
```
