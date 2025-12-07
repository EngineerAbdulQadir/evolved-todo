---
name: performance
description: Optimize code for speed, memory, and scalability. Use after implementing collections/loops or when handling large datasets.
---

# Performance

## Instructions

### When to Use

- After implementing collections/loops
- When handling large datasets (>1000 items)
- Before committing search/filter/sort operations
- When users report slowness

## Algorithmic Complexity (Big-O)

### Target Complexities

| Operation | Target | Acceptable | Avoid |
|-----------|--------|------------|-------|
| Get by ID | O(1) | O(log n) | O(n) |
| Add task | O(1) | O(log n) | O(n) |
| Delete | O(1) | O(log n) | O(n) |
| List all | O(n) | O(n log n) | O(n²) |
| Search | O(n) | O(n log n) | O(n²) |
| Filter | O(n) | O(n log n) | O(n²) |
| Sort | O(n log n) | O(n log n) | O(n²) |

## Examples

### Example 1: Optimization Patterns

```python
# ❌ O(n²) - Nested loops
def find_duplicates(tasks: List[Task]) -> List[Task]:
    duplicates = []
    for i, task1 in enumerate(tasks):
        for task2 in tasks[i+1:]:
            if task1.title == task2.title:
                duplicates.append(task1)
    return duplicates

# ✅ O(n) - Using set
def find_duplicates(tasks: List[Task]) -> List[Task]:
    seen = set()
    duplicates = []
    for task in tasks:
        if task.title in seen:
            duplicates.append(task)
        seen.add(task.title)
    return duplicates
```

## Data Structure Selection

```python
# Fast lookups: Use Dict
tasks_by_id: Dict[int, Task] = {}  # O(1) lookup

# Fast membership: Use Set
completed_ids: Set[int] = {1, 2, 3}  # O(1) membership

# Ordered iteration: Use List
sorted_tasks: List[Task] = []  # O(1) indexing
```

## Benchmarking

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def benchmark(func: Callable[[], T], iterations: int = 1000) -> float:
    """Benchmark function execution time."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    end = time.perf_counter()
    return (end - start) / iterations
```

## Integration with performance-optimizer Subagent

Invoke after implementing operations on collections:

```
Reviews:
- Big-O complexity validation
- Memory usage analysis
- Benchmark critical paths
- Identify bottlenecks
```
