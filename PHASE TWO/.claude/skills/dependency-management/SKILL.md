---
name: dependency-management
description: Manage project dependencies with UV package manager. Use when adding dependencies, updating packages, or performing security audits.
---

# Dependency Management

## Instructions

### When to Use

- Adding new dependencies
- Updating existing packages
- Before committing `pyproject.toml` changes
- Periodic security audits

## UV Package Manager

## Examples

### Example 1: Installing Dependencies

```bash
# Add production dependency
uv add typer
uv add python-dateutil
uv add rich

# Add development dependency
uv add --dev pytest
uv add --dev mypy
uv add --dev ruff

# Add with version constraint
uv add "typer>=0.12.0,<1.0.0"

# Install all dependencies from pyproject.toml
uv sync
```

### pyproject.toml Structure

```toml
[project]
name = "evolved-todo"
version = "0.1.0"
description = "A powerful CLI todo application"
requires-python = ">=3.13"
dependencies = [
    "typer>=0.12.0",
    "python-dateutil>=2.9.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "mypy>=1.11.0",
    "ruff>=0.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "mypy>=1.11.0",
    "ruff>=0.6.0",
]
```

### Dependency Evaluation Criteria

Before adding a dependency, check:

1. **Necessity**: Can we implement this ourselves simply?
2. **Maintenance**: Last update, GitHub stars, open issues
3. **Security**: Known vulnerabilities (CVEs)
4. **License**: Compatible with project license
5. **Size**: Bundle size impact
6. **Dependencies**: Transitive dependencies count

### Security Audits

```bash
# Check for known vulnerabilities
uv run pip-audit

# Update vulnerable packages
uv update <package-name>

# Review dependency tree
uv tree
```

## Integration with dependency-auditor Subagent

Invoke before committing dependency changes:

```
Reviews:
- Dependency necessity and alternatives
- Security vulnerabilities (CVE database)
- License compatibility
- Maintenance status
- Bundle size impact
```

## See Also

- `templates/pyproject-template.toml`
- `scripts/dep-audit.py`
