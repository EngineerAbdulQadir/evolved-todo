# CLI Command Contracts: Phase 1 Complete Todo App

**Date**: 2025-12-06 | **Plan**: [../plan.md](../plan.md)

This document defines the CLI command interface for all 10 Phase 1 features.

---

## Command Overview

```bash
todo                    # Show help
todo add                # Create a new task
todo list               # View/filter/sort tasks
todo show <id>          # View single task details
todo update <id>        # Modify an existing task
todo complete <id>      # Toggle completion status
todo delete <id>        # Remove a task
todo --version          # Show version
todo --help             # Show help
```

---

## 1. Add Task Command

**Features**: 001-Add-Task, 006-Priorities-Tags, 009-Recurring, 010-Due-Dates

### Signature

```bash
todo add <title> [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `title` | string | Yes | Task title (1-200 chars) |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--desc` | `-d` | string | None | Task description (max 1000 chars) |
| `--priority` | `-p` | choice | None | Priority: high, medium, low |
| `--tags` | `-t` | string | None | Comma-separated tags |
| `--due` | `-D` | string | None | Due date (YYYY-MM-DD or natural language) |
| `--time` | `-T` | string | None | Due time (HH:MM or 2:00 PM) |
| `--recur` | `-r` | choice | None | Recurrence: daily, weekly, monthly |
| `--recur-day` | | int | None | Day for weekly (1-7) or monthly (1-31) |

### Examples

```bash
# Basic task
todo add "Buy groceries"

# Task with description
todo add "Prepare presentation" -d "Include Q3 charts and roadmap"

# Task with priority and tags
todo add "Fix login bug" -p high -t "work,urgent"

# Task with due date
todo add "Submit report" -D "2025-12-15"
todo add "Team meeting" -D "tomorrow" -T "2:00 PM"

# Recurring task
todo add "Daily standup" -r daily
todo add "Weekly review" -r weekly --recur-day 1  # Monday
todo add "Pay rent" -r monthly --recur-day 1
```

### Output

**Success:**
```
✓ Task created successfully!
  ID: 1
  Title: Buy groceries
  Priority: medium
  Due: No due date
```

**Error (empty title):**
```
✗ Error: Title cannot be empty
```

**Error (invalid priority):**
```
✗ Error: Invalid priority 'critical'. Must be: high, medium, low
```

---

## 2. List Tasks Command

**Features**: 002-View-Tasks, 007-Search-Filter, 008-Sort-Tasks, 010-Due-Dates

### Signature

```bash
todo list [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--status` | `-s` | choice | all | Filter: all, complete, incomplete |
| `--priority` | `-p` | choice | all | Filter: all, high, medium, low |
| `--tag` | `-t` | string | None | Filter by tag |
| `--due` | `-D` | choice | all | Filter: all, overdue, today, week, none |
| `--search` | `-q` | string | None | Search keyword in title/description |
| `--sort` | | choice | id | Sort by: id, priority, title, due |
| `--desc` | | flag | False | Sort descending |

### Examples

```bash
# View all tasks
todo list

# Filter by status
todo list -s incomplete
todo list -s complete

# Filter by priority
todo list -p high

# Filter by tag
todo list -t work

# Filter by due status
todo list -D overdue
todo list -D today

# Search
todo list -q "meeting"

# Sort
todo list --sort priority
todo list --sort due --desc

# Combined filters
todo list -s incomplete -p high -t work --sort priority
```

### Output

**With tasks:**
```
Tasks (5 of 12 shown)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID  Status  Priority  Title                 Due          Tags
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1   [ ]     HIGH      Fix login bug         Dec 10       work, urgent
3   [ ]     MED       Prepare presentation  Dec 15       work
5   [✓]     LOW       Buy groceries         -            home
7   [ ]     HIGH      Submit report         🚨 OVERDUE   work
9   [ ]     MED       Team meeting ↻        Dec 12       work
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  1 task is overdue!
📅 2 tasks due this week
```

**Notifications (displayed above list):**
```
🚨 "Submit report" is OVERDUE (was due Dec 5)
⚠️  "Fix login bug" is due TODAY
📅 "Prepare presentation" is due in 3 days
```

**Empty list:**
```
No tasks found.
Use 'todo add <title>' to create your first task.
```

**Empty filter results:**
```
No tasks match your filter criteria.
Filters applied: status=incomplete, priority=high, tag=work
```

---

## 3. Show Task Command

**Features**: 002-View-Tasks

### Signature

```bash
todo show <id>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | int | Yes | Task ID to view |

### Example

```bash
todo show 5
```

### Output

```
Task #5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title:       Prepare presentation
Status:      Incomplete [ ]
Priority:    HIGH
Tags:        work, urgent
Due:         Dec 15, 2025 at 2:00 PM
Recurrence:  Weekly (Monday)
Created:     Dec 6, 2025 10:30 AM

Description:
  Include Q3 revenue charts, competitive analysis,
  and 2024 roadmap. Meet with design team first.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Error:**
```
✗ Error: Task with ID 99 not found
```

---

## 4. Update Task Command

**Features**: 003-Update-Task, 006-Priorities-Tags, 009-Recurring, 010-Due-Dates

### Signature

```bash
todo update <id> [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | int | Yes | Task ID to update |

### Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--title` | | string | New title |
| `--desc` | `-d` | string | New description (empty string to remove) |
| `--priority` | `-p` | choice | New priority: high, medium, low |
| `--add-tag` | | string | Add tag(s), comma-separated |
| `--remove-tag` | | string | Remove tag(s), comma-separated |
| `--due` | `-D` | string | New due date (use "none" to remove) |
| `--time` | `-T` | string | New due time (use "none" to remove) |
| `--recur` | `-r` | choice | New recurrence: none, daily, weekly, monthly |
| `--recur-day` | | int | New recurrence day |

### Examples

```bash
# Update title
todo update 5 --title "Prepare Q4 presentation"

# Update description
todo update 5 -d "Updated requirements: include competitor analysis"

# Remove description
todo update 5 -d ""

# Change priority
todo update 5 -p high

# Add/remove tags
todo update 5 --add-tag "priority"
todo update 5 --remove-tag "urgent"

# Update due date
todo update 5 -D "2025-12-20"
todo update 5 -D "next friday" -T "3:00 PM"

# Remove due date
todo update 5 -D none

# Add recurrence
todo update 5 -r weekly --recur-day 5  # Friday

# Remove recurrence
todo update 5 -r none
```

### Output

**Success:**
```
✓ Task #5 updated successfully!
  Title: Prepare Q4 presentation
  Changes: title, priority
```

**Error (not found):**
```
✗ Error: Task with ID 99 not found
```

**Error (empty title):**
```
✗ Error: Title cannot be empty
```

---

## 5. Complete Task Command

**Features**: 004-Mark-Complete, 009-Recurring-Tasks

### Signature

```bash
todo complete <id>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | int | Yes | Task ID to toggle |

### Examples

```bash
todo complete 5
```

### Output

**Mark complete (non-recurring):**
```
✓ Task #5 marked as complete
  "Prepare presentation" [✓]
```

**Mark incomplete:**
```
✓ Task #5 marked as incomplete
  "Prepare presentation" [ ]
```

**Mark complete (recurring task):**
```
✓ Task #5 marked as complete
  "Daily standup" [✓]

↻ Next occurrence created:
  ID: 12
  Due: Dec 7, 2025
```

**Error:**
```
✗ Error: Task with ID 99 not found
```

---

## 6. Delete Task Command

**Features**: 005-Delete-Task

### Signature

```bash
todo delete <id> [OPTIONS]
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | int | Yes | Task ID to delete |

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--force` | `-f` | flag | False | Skip confirmation prompt |

### Examples

```bash
# With confirmation
todo delete 5

# Skip confirmation
todo delete 5 --force
```

### Output

**Confirmation prompt:**
```
⚠️  Delete task #5 "Prepare presentation"?
This action cannot be undone.
Delete? [y/N]: y

✓ Task #5 deleted successfully
```

**Cancelled:**
```
Deletion cancelled.
```

**Force delete:**
```
✓ Task #5 deleted successfully
```

**Error:**
```
✗ Error: Task with ID 99 not found
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (task not found, validation error) |
| 2 | Invalid usage (wrong arguments, invalid options) |

---

## Common Patterns

### Date Input Formats

```
# ISO format
2025-12-15

# Natural language
tomorrow
next monday
dec 15
in 3 days
next week
```

### Time Input Formats

```
# 24-hour
14:00
09:30

# 12-hour
2:00 PM
9:30 AM
```

### Tag Format

```
# Single tag
-t work

# Multiple tags (comma-separated)
-t "work,urgent,priority"
```

### Priority Values

```
high | medium | low
h    | m      | l    # Abbreviations allowed
```

---

## Help Output

```
$ todo --help

Usage: todo [OPTIONS] COMMAND [ARGS]...

Evolved Todo - Phase 1 CLI

A powerful command-line todo application with priorities, tags,
due dates, and recurring tasks.

Options:
  --version  Show version and exit
  --help     Show this message and exit

Commands:
  add       Create a new task
  list      View, filter, and sort tasks
  show      View details of a single task
  update    Modify an existing task
  complete  Toggle task completion status
  delete    Remove a task
```
