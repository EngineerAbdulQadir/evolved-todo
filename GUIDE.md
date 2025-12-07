# Evolved Todo

A spec-driven CLI todo application built with Python, Typer, and Test-Driven Development (TDD).

## Features

- ✅ Create, read, update, and delete tasks
- 🎯 Set task priorities (high, medium, low)
- 🏷️ Organize tasks with tags
- 🔍 Search and filter tasks by multiple criteria
- 📅 Set due dates and times for tasks
- 🔁 Create recurring tasks (daily, weekly, monthly)
- 📊 Sort tasks by various fields
- 💾 In-memory storage with persistence-ready architecture
- ✨ Rich terminal UI with colors and tables

## Requirements

- Python 3.13+
- UV package manager (recommended) or pip

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/evolved-todo.git
cd evolved-todo

# Install dependencies
uv sync

# Install the CLI tool
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/evolved-todo.git
cd evolved-todo

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Usage

### Interactive Menu Mode (Recommended)

The easiest way to use Evolved Todo is through the interactive menu:

```bash
uv run python src/main.py
# or
uv run python -m src.main
```

This launches a user-friendly menu interface:

```
Welcome to the TODO Application!
All data is stored in memory and will be lost when you exit.

============================================================
TODO Application - Interactive Console
============================================================
1) Add Task
2) List Tasks
3) Update Task
4) Delete Task
5) Complete/Uncomplete Task
6) Exit
============================================================

Enter choice (1-6):
```

**Features:**
- Simple numbered menu - just type 1-6
- Step-by-step prompts for all task details
- No need to remember command syntax
- Press Enter to skip optional fields
- All data persists during your session

**Advanced Capabilities:**

**1) Add Task** - Create tasks with all features:
- Title and description
- Priority levels (high/medium/low)
- Tags (comma-separated)
- Due dates and times (YYYY-MM-DD, HH:MM)
- Recurring tasks (daily/weekly/monthly)

**2) List Tasks** - View tasks with advanced filtering and sorting:
- Filter by status (all/complete/incomplete)
- Filter by priority (high/medium/low)
- Filter by tag
- Search by keyword in title/description
- Sort by: id, title, priority, due-date, created
- Sort order: ascending or descending

**3) Update Task** - Modify any task attribute:
- Title and description
- Priority
- Add or remove tags
- Due date and time
- Recurrence pattern and day

**4) Delete Task** - Remove tasks with confirmation

**5) Complete/Uncomplete Task** - Toggle completion (auto-creates next occurrence for recurring tasks)

### Command Line Interface

Alternatively, you can use individual commands:

### Basic Commands

#### Add a task

```bash
# Simple task
todo add "Buy groceries"

# Task with description
todo add "Buy groceries" --desc "Milk, eggs, bread"

# Task with priority
todo add "Fix bug" --priority high

# Task with tags
todo add "Review PR" --tags work,urgent

# Task with due date
todo add "Submit report" --due-date 2025-12-15

# Task with due date and time
todo add "Team meeting" --due-date 2025-12-10 --due-time 14:00
```

#### List tasks

```bash
# List all tasks
todo list

# List incomplete tasks only
todo list --incomplete

# List completed tasks only
todo list --completed

# Filter by priority
todo list --priority high

# Filter by tag
todo list --tag work

# Search by keyword
todo list --search "meeting"

# Sort by due date
todo list --sort due-date

# Sort by priority (descending)
todo list --sort priority --desc
```

#### Update a task

```bash
# Update title
todo update 1 --title "New title"

# Update priority
todo update 1 --priority medium

# Add tags
todo update 1 --add-tags personal,important

# Remove tags
todo update 1 --remove-tags work

# Set due date
todo update 1 --due-date 2025-12-20

# Clear due date
todo update 1 --due-date none
```

#### Complete a task

```bash
# Toggle completion status
todo complete 1

# For recurring tasks, this creates a new task with the next occurrence
```

#### Delete a task

```bash
todo delete 1
```

### Recurring Tasks

Evolved Todo supports recurring tasks that automatically create new instances when completed.

#### Daily recurring task

```bash
todo add "Daily standup" --due-date 2025-12-10 --due-time 09:00 --recur daily
```

When you complete this task, a new task will be created with tomorrow's date.

#### Weekly recurring task

```bash
# Friday team meeting (5 = Friday)
todo add "Team meeting" --due-date 2025-12-12 --recur weekly --recur-day 5
```

When completed, a new task is created for the next Friday.

#### Monthly recurring task

```bash
# Monthly report on the 1st of each month
todo add "Monthly report" --due-date 2025-12-01 --recur monthly --recur-day 1
```

When completed, a new task is created for the 1st of next month.

**Notes:**
- Recurring tasks require a `--due-date`
- Weekly recurrence requires `--recur-day` (1-7 for Monday-Sunday)
- Monthly recurrence requires `--recur-day` (1-31 for day of month)
- To clear recurrence: `todo update 1 --recur none`

### Advanced Filtering and Sorting

#### Combine filters

```bash
# High priority work tasks
todo list --priority high --tag work

# Incomplete tasks with "meeting" in title
todo list --incomplete --search meeting
```

#### Sort options

Available sort fields:
- `id` - Task ID (default)
- `title` - Task title (alphabetical)
- `priority` - Priority level (high → medium → low → none)
- `due-date` - Due date and time (earliest first)
- `created` - Creation date (newest first when using `--desc`)

```bash
# Show tasks by priority
todo list --sort priority

# Show tasks by due date (descending)
todo list --sort due-date --desc

# Show recently created tasks
todo list --sort created --desc
```

### Getting Help

```bash
# General help
todo --help

# Command-specific help
todo add --help
todo list --help
todo update --help
```

## Examples

### Example 1: Plan your day

```bash
# Add morning tasks
todo add "Morning standup" --due-date 2025-12-10 --due-time 09:00 --priority high --tags work
todo add "Review PRs" --due-date 2025-12-10 --due-time 10:00 --tags work

# Add personal task
todo add "Gym" --due-date 2025-12-10 --due-time 18:00 --tags personal

# View today's tasks sorted by due time
todo list --sort due-date
```

### Example 2: Weekly team meeting

```bash
# Create recurring weekly meeting
todo add "Team retrospective" \
  --desc "Review sprint progress and plan improvements" \
  --due-date 2025-12-12 \
  --due-time 15:00 \
  --recur weekly \
  --recur-day 5 \
  --priority medium \
  --tags work,meeting

# When you complete it, a new task is automatically created for next Friday
todo complete 1
```

### Example 3: Track project tasks

```bash
# Add project tasks with tags
todo add "Setup CI/CD" --priority high --tags devops,project-alpha
todo add "Write API tests" --priority high --tags testing,project-alpha
todo add "Update documentation" --priority low --tags docs,project-alpha

# View all project-alpha tasks
todo list --tag project-alpha

# View high-priority project tasks
todo list --tag project-alpha --priority high
```

### Example 4: Monthly recurring tasks

```bash
# Bill payments on the 1st of each month
todo add "Pay rent" --due-date 2025-12-01 --recur monthly --recur-day 1 --priority high
todo add "Review subscriptions" --due-date 2025-12-15 --recur monthly --recur-day 15

# When completed, new tasks are created for next month
```

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_task_service.py

# Run with verbose output
uv run pytest -v
```

### Quality Checks

```bash
# Type checking with mypy
uv run mypy --strict src

# Linting with ruff
uv run ruff check src

# Format checking
uv run ruff format --check src

# Auto-format code
uv run ruff format src
```

### Project Structure

```
evolved-todo/
├── src/
│   ├── models/          # Data models (Task, Priority, etc.)
│   ├── services/        # Business logic (TaskService, RecurrenceService, etc.)
│   ├── lib/             # Utilities (IdGenerator, etc.)
│   ├── cli/             # CLI commands and formatting
│   └── main.py          # Application entry point
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── specs/               # Feature specifications
└── pyproject.toml       # Project configuration
```

## Architecture

Evolved Todo follows clean architecture principles:

- **Models** - Data structures with validation
- **Services** - Business logic and operations
- **CLI** - User interface layer
- **Storage** - Abstracted storage layer (currently in-memory)

All features are built using Test-Driven Development (TDD) with >85% code coverage.

## Contributing

This project was built following Spec-Driven Development (SDD) methodology. All features are documented in the `specs/` directory with comprehensive acceptance criteria and test cases.

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [pytest](https://pytest.org/) - Testing framework
- [mypy](https://mypy-lang.org/) - Static type checking
- [ruff](https://docs.astral.sh/ruff/) - Linting and formatting
