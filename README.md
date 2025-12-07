# Evolved Todo - Interactive Menu Guide

Welcome to the Evolved Todo Interactive Menu! This guide provides step-by-step examples for every feature.

## Getting Started

To start the interactive menu:

```bash
cd evolved-todo
uv run python src/main.py
```

You'll see the main menu:

```
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

---

## 1) Add Task - Create Tasks with All Features

### Example 1.1: Basic Task (Title Only)

**Scenario**: Add a simple task with just a title.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Buy groceries
Description (optional, press Enter to skip): [Press Enter]
Priority (high/medium/low, press Enter to skip): [Press Enter]
Tags (comma-separated, press Enter to skip): [Press Enter]
Due date (YYYY-MM-DD, press Enter to skip): [Press Enter]

✓ Task created: Buy groceries (ID: 1)
```

### Example 1.2: Task with Description

**Scenario**: Add a task with both title and description.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Prepare presentation
Description (optional, press Enter to skip): Include Q3 charts and metrics
Priority (high/medium/low, press Enter to skip): [Press Enter]
Tags (comma-separated, press Enter to skip): [Press Enter]
Due date (YYYY-MM-DD, press Enter to skip): [Press Enter]

✓ Task created: Prepare presentation (ID: 2)
```

### Example 1.3: Task with Priority

**Scenario**: Add a high-priority task.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Fix critical bug
Description (optional, press Enter to skip): Database connection timeout
Priority (high/medium/low, press Enter to skip): high
Tags (comma-separated, press Enter to skip): [Press Enter]
Due date (YYYY-MM-DD, press Enter to skip): [Press Enter]

✓ Task created: Fix critical bug (ID: 3)
```

**Priority Options**:
- `high` - Red priority indicator
- `medium` - Yellow priority indicator
- `low` - Dim priority indicator
- Press Enter - No priority

### Example 1.4: Task with Tags

**Scenario**: Add a task with multiple tags.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Review pull requests
Description (optional, press Enter to skip): Check code quality and tests
Priority (high/medium/low, press Enter to skip): medium
Tags (comma-separated, press Enter to skip): work, code-review, urgent
Due date (YYYY-MM-DD, press Enter to skip): [Press Enter]

✓ Task created: Review pull requests (ID: 4)
```

**Tag Tips**:
- Separate multiple tags with commas
- Spaces around commas are automatically trimmed
- Tags are displayed in blue in the task list
- Maximum 10 tags per task
- Each tag can be up to 50 characters

### Example 1.5: Task with Due Date

**Scenario**: Add a task due on a specific date.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Submit quarterly report
Description (optional, press Enter to skip): Financial summary for Q4
Priority (high/medium/low, press Enter to skip): high
Tags (comma-separated, press Enter to skip): work, report
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-15

✓ Task created: Submit quarterly report (ID: 5)
```

**Due Date Format**: `YYYY-MM-DD` (e.g., 2025-12-15)

### Example 1.6: Task with Due Date and Time

**Scenario**: Add a task with both date and specific time.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Team meeting
Description (optional, press Enter to skip): Discuss sprint planning
Priority (high/medium/low, press Enter to skip): medium
Tags (comma-separated, press Enter to skip): work, meeting
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-10
Due time (HH:MM, press Enter to skip): 14:00

✓ Task created: Team meeting (ID: 6)
```

**Due Time Format**: `HH:MM` in 24-hour format (e.g., 14:00 for 2:00 PM)

**Note**: Due time is only asked if you provide a due date.

### Example 1.7: Daily Recurring Task

**Scenario**: Create a task that repeats every day.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Daily standup
Description (optional, press Enter to skip): Morning team sync
Priority (high/medium/low, press Enter to skip): high
Tags (comma-separated, press Enter to skip): work, meeting
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-10
Due time (HH:MM, press Enter to skip): 09:00
Recurrence (daily/weekly/monthly, press Enter to skip): daily

✓ Task created: Daily standup (ID: 7)
```

**Important**: Recurring tasks require a due date!

When you complete this task, a new task will be automatically created for the next day.

### Example 1.8: Weekly Recurring Task

**Scenario**: Create a task that repeats every Friday.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Weekly team retrospective
Description (optional, press Enter to skip): Review sprint progress
Priority (high/medium/low, press Enter to skip): medium
Tags (comma-separated, press Enter to skip): work, meeting
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-12
Due time (HH:MM, press Enter to skip): 15:00
Recurrence (daily/weekly/monthly, press Enter to skip): weekly
Recurrence day (1-7 for Mon-Sun): 5

✓ Task created: Weekly team retrospective (ID: 8)
```

**Recurrence Day for Weekly**:
- `1` = Monday
- `2` = Tuesday
- `3` = Wednesday
- `4` = Thursday
- `5` = Friday
- `6` = Saturday
- `7` = Sunday

### Example 1.9: Monthly Recurring Task

**Scenario**: Create a task that repeats on the 1st of every month.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Pay rent
Description (optional, press Enter to skip): Monthly rent payment
Priority (high/medium/low, press Enter to skip): high
Tags (comma-separated, press Enter to skip): personal, finance
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-01
Due time (HH:MM, press Enter to skip): [Press Enter]
Recurrence (daily/weekly/monthly, press Enter to skip): monthly
Recurrence day (1-31): 1

✓ Task created: Pay rent (ID: 9)
```

**Recurrence Day for Monthly**:
- Enter a day number from `1` to `31`
- If the month doesn't have that day (e.g., February 31), it will use the last day of the month

### Example 1.10: Complete Task with All Features

**Scenario**: Create a fully-featured task with every option.

```
Enter choice (1-6): 1

--- Add New Task ---

Title (required): Complete project milestone
Description (optional, press Enter to skip): Finalize design documents and get approval
Priority (high/medium/low, press Enter to skip): high
Tags (comma-separated, press Enter to skip): work, project-alpha, urgent
Due date (YYYY-MM-DD, press Enter to skip): 2025-12-20
Due time (HH:MM, press Enter to skip): 17:00
Recurrence (daily/weekly/monthly, press Enter to skip): [Press Enter]

✓ Task created: Complete project milestone (ID: 10)
```

---

## 2) List Tasks - View Tasks with Advanced Filtering and Sorting

### Example 2.1: List All Tasks (Basic)

**Scenario**: View all tasks without any filters.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter for all]
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 1      │ [ ]      │ -        │ Buy    │ -                  │ -     │        │
│        │          │          │ groce… │                    │       │        │
│ 2      │ [ ]      │ -        │ Prepa… │ -                  │ -     │ Incl…  │
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
│        │          │          │ criti… │                    │       │        │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Example 2.2: Filter by Status - Incomplete Only

**Scenario**: View only incomplete tasks.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): incomplete
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

Showing 8 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 1      │ [ ]      │ -        │ Buy    │ -                  │ -     │        │
│ 2      │ [ ]      │ -        │ Prepa… │ -                  │ -     │ Incl…  │
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Status Options**:
- `all` - Show all tasks (default)
- `complete` - Show only completed tasks (marked with [X])
- `incomplete` - Show only incomplete tasks (marked with [ ])

### Example 2.3: Filter by Status - Completed Only

**Scenario**: View only completed tasks.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): complete
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

Showing 2 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 5      │ [X]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│ 7      │ [X]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Example 2.4: Filter by Priority

**Scenario**: View only high-priority tasks.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter]
Filter by priority (high/medium/low, Enter to skip): high
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

Showing 4 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
│ 5      │ [ ]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│ 9      │ [ ]      │ HIGH     │ Pay    │ Dec 01             │ pers… │ Mont…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Priority Filter Options**:
- `high` - Show only high-priority tasks
- `medium` - Show only medium-priority tasks
- `low` - Show only low-priority tasks
- Press Enter - Show all priorities

### Example 2.5: Filter by Tag

**Scenario**: View only tasks tagged with "work".

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter]
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): work
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

Showing 5 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 4      │ [ ]      │ MED      │ Review │ -                  │ work  │ Check… │
│ 5      │ [ ]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│ 6      │ [ ]      │ MED      │ Team   │ Dec 10 02:00 PM    │ work  │ Disc…  │
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│ 8      │ [ ]      │ MED      │ Weekly │ Dec 12 03:00 PM    │ work  │ Revi…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Example 2.6: Search by Keyword

**Scenario**: Search for tasks containing "meeting" in title or description.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter]
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): meeting
Sort by (id/title/priority/due-date/created, Enter for id): [Press Enter]
Sort order (asc/desc, Enter for asc): [Press Enter]

Showing 2 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 6      │ [ ]      │ MED      │ Team   │ Dec 10 02:00 PM    │ work  │ Disc…  │
│        │          │          │ meeti… │                    │       │ spri…  │
│ 8      │ [ ]      │ MED      │ Weekly │ Dec 12 03:00 PM    │ work  │ Revi…  │
│        │          │          │ team   │                    │ meeti │ spri…  │
│        │          │          │ retro… │                    │       │ prog…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Search Tips**:
- Search is case-insensitive
- Searches both title AND description
- Matches partial words (e.g., "meet" finds "meeting")

### Example 2.7: Sort by Priority (Descending)

**Scenario**: View tasks sorted by priority (highest first).

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter]
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): priority
Sort order (asc/desc, Enter for asc): desc

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
│ 5      │ [ ]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│ 9      │ [ ]      │ HIGH     │ Pay    │ Dec 01             │ pers… │ Mont…  │
│ 4      │ [ ]      │ MED      │ Review │ -                  │ work  │ Check… │
│ 6      │ [ ]      │ MED      │ Team   │ Dec 10 02:00 PM    │ work  │ Disc…  │
│ 8      │ [ ]      │ MED      │ Weekly │ Dec 12 03:00 PM    │ work  │ Revi…  │
│ 1      │ [ ]      │ -        │ Buy    │ -                  │ -     │        │
│ 2      │ [ ]      │ -        │ Prepa… │ -                  │ -     │ Incl…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Sort By Options**:
- `id` - Sort by task ID (default)
- `title` - Sort alphabetically by title
- `priority` - Sort by priority level (high → medium → low → none)
- `due-date` - Sort by due date (earliest first)
- `created` - Sort by creation date

**Sort Order Options**:
- `asc` - Ascending (default)
- `desc` - Descending

### Example 2.8: Sort by Due Date (Ascending)

**Scenario**: View tasks sorted by due date (earliest first).

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): incomplete
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): due-date
Sort order (asc/desc, Enter for asc): asc

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 9      │ [ ]      │ HIGH     │ Pay    │ ⚠ Dec 01           │ pers… │ Mont…  │
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│ 6      │ [ ]      │ MED      │ Team   │ Dec 10 02:00 PM    │ work  │ Disc…  │
│ 8      │ [ ]      │ MED      │ Weekly │ Dec 12 03:00 PM    │ work  │ Revi…  │
│ 5      │ [ ]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│ 1      │ [ ]      │ -        │ Buy    │ -                  │ -     │        │
│ 2      │ [ ]      │ -        │ Prepa… │ -                  │ -     │ Incl…  │
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Due Date Indicators**:
- `⚠` (Red) - Task is overdue
- `●` (Yellow) - Task is due today
- No indicator - Task is due in the future
- Tasks without due dates appear at the end

### Example 2.9: Sort by Title (Alphabetically)

**Scenario**: View tasks sorted alphabetically by title.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): [Press Enter]
Filter by priority (high/medium/low, Enter to skip): [Press Enter]
Filter by tag (Enter to skip): [Press Enter]
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): title
Sort order (asc/desc, Enter for asc): asc

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 1      │ [ ]      │ -        │ Buy    │ -                  │ -     │        │
│        │          │          │ groce… │                    │       │        │
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│        │          │          │ standu │                    │ meeti │        │
│ 3      │ [ ]      │ HIGH     │ Fix    │ -                  │ -     │ Data…  │
│        │          │          │ criti… │                    │       │        │
│ 9      │ [ ]      │ HIGH     │ Pay    │ Dec 01             │ pers… │ Mont…  │
│        │          │          │ rent   │                    │ finan │        │
│ 2      │ [ ]      │ -        │ Prepa… │ -                  │ -     │ Incl…  │
│        │          │          │ prese… │                    │       │        │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Example 2.10: Combined Filters and Sorting

**Scenario**: Find incomplete, high-priority work tasks, sorted by due date.

```
Enter choice (1-6): 2

--- List Tasks ---
Press Enter to skip filters and use defaults

Show (all/complete/incomplete): incomplete
Filter by priority (high/medium/low, Enter to skip): high
Filter by tag (Enter to skip): work
Search keyword (Enter to skip): [Press Enter]
Sort by (id/title/priority/due-date/created, Enter for id): due-date
Sort order (asc/desc, Enter for asc): asc

Showing 2 of 10 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 7      │ [ ]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│        │          │          │ standu │                    │ meeti │        │
│ 5      │ [ ]      │ HIGH     │ Submi… │ Dec 15             │ work  │ Fina…  │
│        │          │          │ quart… │                    │ repor │        │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

This example shows how filters work with AND logic - all conditions must be met.

---

## 3) Update Task - Modify Any Task Attribute

### Example 3.1: Update Title Only

**Scenario**: Change the title of task #1.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 1

Current: Buy groceries
Press Enter to keep current value

New title (Enter to keep): Buy groceries and household items
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Buy groceries and household items
```

### Example 3.2: Update Description

**Scenario**: Add a description to task #1.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 1

Current: Buy groceries and household items
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): Milk, eggs, bread, and cleaning supplies
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Buy groceries and household items
```

### Example 3.3: Update Priority

**Scenario**: Change task #2 from no priority to high priority.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 2

Current: Prepare presentation
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): high
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Prepare presentation
```

**Priority Update Options**:
- `high` - Set to high priority
- `medium` - Set to medium priority
- `low` - Set to low priority
- `none` - Remove priority
- Press Enter - Keep current priority

### Example 3.4: Add Tags to Task

**Scenario**: Add tags to task #2.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 2

Current: Prepare presentation
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): work, presentation, Q4
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Prepare presentation
```

### Example 3.5: Remove Tags from Task

**Scenario**: Remove the "Q4" tag from task #2.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 2

Current: Prepare presentation
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): Q4
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Prepare presentation
```

**Tag Update Tips**:
- You can add and remove tags in the same update
- Existing tags remain unless explicitly removed
- Duplicate tags are automatically prevented

### Example 3.6: Add Both Tags

**Scenario**: Add some tags and remove others simultaneously.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 4

Current: Review pull requests
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): github, review
Remove tags (comma-separated, Enter to skip): urgent
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Review pull requests
```

Result: Task now has tags: `work, code-review, github, review` (removed `urgent`, added `github` and `review`)

### Example 3.7: Set Due Date

**Scenario**: Add a due date to task #1.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 1

Current: Buy groceries and household items
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): 2025-12-08
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Buy groceries and household items
```

### Example 3.8: Set Due Time

**Scenario**: Add a specific time to the due date.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 1

Current: Buy groceries and household items
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): 18:00
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Buy groceries and household items
```

Result: Task now has due date: Dec 08, 2025 at 6:00 PM

### Example 3.9: Clear Due Date

**Scenario**: Remove the due date from task #1.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 1

Current: Buy groceries and household items
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): none
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Buy groceries and household items
```

**Note**: Setting due date to 'none' also clears the due time.

### Example 3.10: Add Weekly Recurrence

**Scenario**: Make task #6 recur every Friday.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 6

Current: Team meeting
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): weekly
Recurrence day (1-7 for Mon-Sun): 5

✓ Task updated: Team meeting
```

**Important**: Task must have a due date before adding recurrence.

### Example 3.11: Change Recurrence Pattern

**Scenario**: Change task #7 from daily to weekly recurrence.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 7

Current: Daily standup
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): weekly
Recurrence day (1-7 for Mon-Sun): 2

✓ Task updated: Daily standup
```

Result: Task now recurs every Tuesday instead of daily.

### Example 3.12: Remove Recurrence

**Scenario**: Stop task #7 from recurring.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 7

Current: Daily standup
Press Enter to keep current value

New title (Enter to keep): [Press Enter]
New description (Enter to keep): [Press Enter]
New priority (high/medium/low/none, Enter to keep): [Press Enter]
Add tags (comma-separated, Enter to skip): [Press Enter]
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): [Press Enter]
New due time (HH:MM or 'none', Enter to keep): [Press Enter]
New recurrence (daily/weekly/monthly/none, Enter to keep): none

✓ Task updated: Daily standup
```

### Example 3.13: Update Multiple Fields at Once

**Scenario**: Change multiple attributes of task #3 in one update.

```
Enter choice (1-6): 3

--- Update Task ---

Task ID to update: 3

Current: Fix critical bug
Press Enter to keep current value

New title (Enter to keep): Fix database connection timeout
New description (Enter to keep): Issue occurs during peak hours, needs urgent fix
New priority (high/medium/low/none, Enter to keep): high
Add tags (comma-separated, Enter to skip): urgent, bug, database
Remove tags (comma-separated, Enter to skip): [Press Enter]
New due date (YYYY-MM-DD or 'none', Enter to keep): 2025-12-08
New due time (HH:MM or 'none', Enter to keep): 17:00
New recurrence (daily/weekly/monthly/none, Enter to keep): [Press Enter]

✓ Task updated: Fix database connection timeout
```

Result: Updated title, description, priority remains high, added 3 tags, set due date and time.

---

## 4) Delete Task - Remove Tasks with Confirmation

### Example 4.1: Delete Task with Confirmation

**Scenario**: Delete task #1 with confirmation prompt.

```
Enter choice (1-6): 4

--- Delete Task ---

Task ID to delete: 1
Delete task #1: 'Buy groceries and household items'? (y/n): y

✓ Task #1 deleted
```

### Example 4.2: Cancel Deletion

**Scenario**: Start to delete a task but change your mind.

```
Enter choice (1-6): 4

--- Delete Task ---

Task ID to delete: 2
Delete task #2: 'Prepare presentation'? (y/n): n

Deletion cancelled
```

### Example 4.3: Delete Non-Existent Task

**Scenario**: Try to delete a task that doesn't exist.

```
Enter choice (1-6): 4

--- Delete Task ---

Task ID to delete: 999

✗ Error: Task with ID 999 not found
```

### Example 4.4: Delete Completed Task

**Scenario**: Delete a task you've already completed.

```
Enter choice (1-6): 4

--- Delete Task ---

Task ID to delete: 5
Delete task #5: 'Submit quarterly report'? (y/n): y

✓ Task #5 deleted
```

**Note**: You can delete both complete and incomplete tasks.

---

## 5) Complete/Uncomplete Task - Toggle Completion

### Example 5.1: Complete a Basic Task

**Scenario**: Mark task #1 as complete.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 1

✓ Task #1 completed
```

The task now shows `[X]` (green checkmark) in the task list.

### Example 5.2: Uncomplete a Task

**Scenario**: Mark task #1 as incomplete again.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 1

✓ Task #1 marked incomplete
```

The task now shows `[ ]` (empty checkbox) in the task list.

### Example 5.3: Complete Daily Recurring Task

**Scenario**: Complete task #7 (Daily standup) which recurs daily.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 7

✓ Task #7 completed

--- Then check the task list ---

Enter choice (1-6): 2

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 7      │ [X]      │ HIGH     │ Daily  │ Dec 10 09:00 AM    │ work  │ Morn…  │
│        │          │          │ standu │                    │ meeti │        │
│ 11     │ [ ]      │ HIGH     │ Daily  │ Dec 11 09:00 AM    │ work  │ Morn…  │
│        │          │          │ standu │                    │ meeti │        │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Result**:
- Task #7 is marked complete
- A NEW task #11 is created for tomorrow (Dec 11) with the same details
- The new task is incomplete and ready for tomorrow

### Example 5.4: Complete Weekly Recurring Task

**Scenario**: Complete task #8 (Weekly team retrospective) which recurs every Friday.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 8

✓ Task #8 completed

--- Then check the task list ---

Enter choice (1-6): 2

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 8      │ [X]      │ MED      │ Weekly │ Dec 12 03:00 PM    │ work  │ Revi…  │
│        │          │          │ team   │                    │ meeti │ spri…  │
│ 12     │ [ ]      │ MED      │ Weekly │ Dec 19 03:00 PM    │ work  │ Revi…  │
│        │          │          │ team   │                    │ meeti │ spri…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Result**:
- Task #8 is marked complete
- A NEW task #12 is created for next Friday (Dec 19) with the same details

### Example 5.5: Complete Monthly Recurring Task

**Scenario**: Complete task #9 (Pay rent) which recurs on the 1st of every month.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 9

✓ Task #9 completed

--- Then check the task list ---

Enter choice (1-6): 2

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 9      │ [X]      │ HIGH     │ Pay    │ Dec 01             │ pers… │ Mont…  │
│        │          │          │ rent   │                    │ finan │        │
│ 13     │ [ ]      │ HIGH     │ Pay    │ Jan 01             │ pers… │ Mont…  │
│        │          │          │ rent   │                    │ finan │        │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Result**:
- Task #9 is marked complete
- A NEW task #13 is created for next month (Jan 01) with the same details

### Example 5.6: Complete Non-Recurring Task

**Scenario**: Complete task #2 which doesn't recur.

```
Enter choice (1-6): 5

--- Complete/Uncomplete Task ---

Task ID to toggle: 2

✓ Task #2 completed

--- Then check the task list ---

Enter choice (1-6): 2

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 2      │ [X]      │ HIGH     │ Prepa… │ -                  │ work  │ Incl…  │
│        │          │          │ prese… │                    │ pres… │ Q3     │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

**Result**:
- Task #2 is marked complete
- NO new task is created (this task doesn't recur)

### Example 5.7: Toggle Task Multiple Times

**Scenario**: Mark a task complete, then incomplete, then complete again.

```
--- First toggle: Complete ---
Enter choice (1-6): 5
Task ID to toggle: 3
✓ Task #3 completed

--- Second toggle: Uncomplete ---
Enter choice (1-6): 5
Task ID to toggle: 3
✓ Task #3 marked incomplete

--- Third toggle: Complete again ---
Enter choice (1-6): 5
Task ID to toggle: 3
✓ Task #3 completed
```

**Note**: You can toggle completion status as many times as needed.

---

## 6) Exit - Close the Application

### Example 6.1: Exit the Application

**Scenario**: Close the todo application.

```
Enter choice (1-6): 6

Goodbye!
```

**Important**: All data is stored in memory and will be lost when you exit. If you want to persist your tasks, consider implementing file-based storage or database persistence.

---

## Complete Workflow Example

Here's a complete workflow showing how to use multiple features together:

### Step 1: Start the Application

```bash
uv run python src/main.py
```

### Step 2: Add Work Tasks for the Week

```
Enter choice (1-6): 1

--- Add Task: Monday Meeting ---
Title: Weekly standup
Description: Team sync meeting
Priority: high
Tags: work, meeting
Due date: 2025-12-08
Due time: 09:00
Recurrence: weekly
Recurrence day: 1

✓ Task created: Weekly standup (ID: 1)
```

```
Enter choice (1-6): 1

--- Add Task: Project Work ---
Title: Complete feature X
Description: Implement user authentication
Priority: high
Tags: work, project-alpha, development
Due date: 2025-12-12
Due time: [Press Enter]
Recurrence: [Press Enter]

✓ Task created: Complete feature X (ID: 2)
```

### Step 3: Add Personal Tasks

```
Enter choice (1-6): 1

--- Add Task: Personal ---
Title: Gym workout
Description: [Press Enter]
Priority: medium
Tags: personal, health
Due date: [Press Enter]
Recurrence: [Press Enter]

✓ Task created: Gym workout (ID: 3)
```

### Step 4: View All Work Tasks

```
Enter choice (1-6): 2

--- List Tasks ---
Show: incomplete
Filter by priority: [Press Enter]
Filter by tag: work
Search keyword: [Press Enter]
Sort by: due-date
Sort order: asc

Showing 2 of 3 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 1      │ [ ]      │ HIGH     │ Weekly │ Dec 08 09:00 AM    │ work  │ Team…  │
│ 2      │ [ ]      │ HIGH     │ Compl… │ Dec 12             │ work  │ Impl…  │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Step 5: Complete the Meeting

```
Enter choice (1-6): 5

Task ID to toggle: 1

✓ Task #1 completed
```

A new task #4 is created for next Monday!

### Step 6: Update Project Task

```
Enter choice (1-6): 3

Task ID to update: 2
New title: [Press Enter]
New description: Add JWT authentication and tests
New priority: [Press Enter]
Add tags: testing, backend
Remove tags: [Press Enter]
New due date: [Press Enter]
New due time: [Press Enter]
New recurrence: [Press Enter]

✓ Task updated: Complete feature X
```

### Step 7: View High-Priority Tasks Due This Week

```
Enter choice (1-6): 2

Show: incomplete
Filter by priority: high
Filter by tag: [Press Enter]
Search keyword: [Press Enter]
Sort by: due-date
Sort order: asc

Showing 2 of 4 tasks

                                     Tasks
┌────────┬──────────┬──────────┬────────┬────────────────────┬───────┬────────┐
│ ID     │ Status   │ Priority │ Title  │ Due Date           │ Tags  │ Descr… │
├────────┼──────────┼──────────┼────────┼────────────────────┼───────┼────────┤
│ 4      │ [ ]      │ HIGH     │ Weekly │ Dec 15 09:00 AM    │ work  │ Team…  │
│ 2      │ [ ]      │ HIGH     │ Compl… │ Dec 12             │ work  │ Add…   │
└────────┴──────────┴──────────┴────────┴────────────────────┴───────┴────────┘
```

### Step 8: Exit

```
Enter choice (1-6): 6

Goodbye!
```

---

## Tips and Best Practices

### 1. **Use Tags Effectively**
- Create a consistent tagging system (e.g., `work`, `personal`, `urgent`, `project-name`)
- Use tags to group related tasks across projects
- Filter by tag to focus on specific areas

### 2. **Leverage Priorities**
- Use `high` for urgent/critical tasks
- Use `medium` for important but not urgent tasks
- Use `low` for nice-to-have tasks
- Leave priority empty for casual tasks

### 3. **Set Due Dates Wisely**
- Add due dates to time-sensitive tasks
- Use due times for meetings and appointments
- Leave due dates empty for tasks without deadlines

### 4. **Use Recurring Tasks for Routines**
- Set up daily recurring tasks for daily habits
- Use weekly recurring tasks for regular meetings
- Create monthly recurring tasks for bills and reports

### 5. **Combine Filters for Focus**
- Filter incomplete + high-priority + specific tag for urgent work
- Filter by tag + sort by due-date for project planning
- Search keywords to find related tasks across projects

### 6. **Update Instead of Delete**
- If plans change, update the task instead of deleting
- Add notes to descriptions to track progress
- Adjust due dates as needed

### 7. **Regular Review**
- List all incomplete tasks weekly
- Complete or update tasks that are no longer relevant
- Adjust priorities based on current needs

---

## Keyboard Shortcuts and Tips

### Quick Tips:
- Press **Enter** to skip optional fields
- Type **6** anytime to exit safely
- Invalid inputs show helpful error messages
- All data persists during your session

### Common Workflows:
1. **Morning routine**: List incomplete → Sort by due-date
2. **End of day**: Complete finished tasks → Review tomorrow's tasks
3. **Weekly planning**: List by tag → Sort by priority → Update due dates
4. **Project focus**: Filter by tag + priority → Sort by due-date

---

## Troubleshooting

### "Task with ID X not found"
- The task may have been deleted
- Double-check the task ID in the list

### "Invalid priority"
- Use lowercase: `high`, `medium`, or `low`
- Or type `none` to remove priority

### "Invalid date format"
- Use format: `YYYY-MM-DD` (e.g., 2025-12-15)
- Use 4-digit year, 2-digit month, 2-digit day

### "Invalid time format"
- Use format: `HH:MM` in 24-hour time (e.g., 14:00)
- Use 2 digits for hours and minutes

### "Recurring tasks require a due date"
- Add a due date first, then set recurrence
- Or update an existing task to add both

---

## Summary

This guide covered all features of the Evolved Todo interactive menu:

✅ **Add Task** - Create tasks with titles, descriptions, priorities, tags, due dates/times, and recurrence
✅ **List Tasks** - Filter by status, priority, tag, search keywords, and sort by any field
✅ **Update Task** - Modify any attribute including tags and recurrence settings
✅ **Delete Task** - Remove tasks with confirmation
✅ **Complete Task** - Toggle completion and auto-create recurring task instances

For command-line usage and additional information, see the [README.md](README.md) file.

---

**Happy task managing! 🎯**
