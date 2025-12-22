# ADR-001: CLI Framework Selection

**Date**: 2025-12-06
**Status**: Accepted
**Deciders**: Engineer Abdul Qadir
**Feature**: Phase 1 Todo App (All Features)

## Context

The Phase 1 Todo App requires a CLI framework to handle:
- Command parsing (add, list, update, complete, delete)
- Argument and option handling (--title, --desc, --priority, etc.)
- Help text generation
- Input validation
- Type safety alignment with mypy strict mode

The constitution mandates Python 3.13+ and strict type checking.

## Decision

**Use `typer` as the CLI framework.**

```python
import typer

app = typer.Typer(help="Evolved Todo - Phase 1 CLI")

@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    description: str = typer.Option(None, "--desc", "-d"),
) -> None:
    """Add a new task."""
    ...
```

## Consequences

### Positive
- **Type-safe**: Built on Python type hints, aligns perfectly with mypy strict mode
- **Auto-documentation**: Generates help text from function signatures and docstrings
- **Minimal boilerplate**: Decorators handle all argument parsing
- **Modern Python**: Designed for Python 3.6+, works great with 3.13
- **Rich integration**: Built-in support for `rich` library for colored output
- **Click foundation**: Built on Click, inheriting its stability and community support

### Negative
- **External dependency**: Not part of standard library (requires installation)
- **Learning curve**: Developers unfamiliar with typer need to learn its patterns
- **Abstraction layer**: Less control than raw argparse for edge cases

### Neutral
- Adds ~50KB to project dependencies
- Well-maintained with regular updates

## Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|--------------|
| `argparse` | Standard library, no deps | Verbose, manual help text, no type inference | Too much boilerplate, doesn't leverage type hints |
| `click` | Mature, flexible, well-documented | More verbose than Typer, decorator-heavy | Typer wraps Click with better developer experience |
| `fire` | Zero configuration, auto-generates CLI | Less control over help/validation, magic behavior | Insufficient validation control for our requirements |
| `docopt` | Elegant docstring-based | Less type-safe, limited validation | Doesn't align with mypy strict requirements |

## Compliance

- **Constitution II (Test-First)**: Typer commands are easily testable via CliRunner
- **Constitution IV (Technology Stack)**: Python 3.13+ compatible
- **Constitution VI (Type Safety)**: Full type annotation support

## References

- [Typer Documentation](https://typer.tiangolo.com/)
- [research.md Section 1](../specs/001-phase1-todo-app/research.md#1-cli-framework-selection)
