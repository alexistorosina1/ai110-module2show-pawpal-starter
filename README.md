# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

# Today's Schedule

Daily plan for Sam (55/60 min used):

- Feeding for Mittens (10 min) [priority: high]
- Morning walk for Biscuit (30 min) [priority: high]
- Litter cleanup for Mittens (15 min) [priority: medium]
  Skipped — not enough time left:
- Grooming for Biscuit (20 min) [priority: low]
  Reasoning: tasks are ordered by priority (high first), then by shortest duration, and added until the time budget runs out.

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

`pytest.ini` sets `pythonpath = .`, so the command works without any extra
environment setup.

### What the tests cover

The suite in `tests/test_pawpal.py` verifies the core scheduling behaviors:

- **Task completion** — `mark_complete()` flips a task's status to completed.
- **Task assignment** — adding a task to a `Pet` increases that pet's task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological
  order, with untimed tasks sorting last.
- **Recurrence logic** — completing a `"daily"` task auto-spawns a new instance
  dated one day later, reset to not-completed.
- **Conflict detection** — `detect_conflicts()` flags tasks that share the exact
  same start time (and leaves non-clashing tasks alone).

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/alexistorosina/Desktop/codepath/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.0
collected 5 items

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.04s ===============================
```

### Confidence Level

**★★★★☆ (4/5)** — The most important scheduling behaviors (sorting, recurrence,
and conflict detection) are verified and passing. Confidence is held at 4 rather
than 5 because some edge cases are not yet covered: the time-budget greedy
selector (`filter_by_time`), interval-overlap detection (`detect_overlaps`),
month/year date rollovers for recurring tasks, and the `date.today()` fallback
when a recurring task has no explicit date.

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py` (classes `Task`, `Pet`, `Owner`,
`Scheduler`). Each feature below names the method that implements it.

| Feature                     | Method(s)                                          | Notes                                                                   |
| --------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------- |
| Sort by priority            | `Scheduler.sort_tasks()`                           | Orders pending tasks by priority rank, then shortest duration.          |
| Sort by time                | `Scheduler.sort_by_time()`                         | Chronological by `"HH:MM"` start; untimed tasks sort last.              |
| Filter by pet / status      | `Scheduler.filter_tasks()`                         | Optional `pet_name` and/or `completed` filters; both optional.          |
| Filter by time budget       | `Scheduler.filter_by_time()`                       | Greedily keeps tasks that fit within the owner's `available_mins`.      |
| Recurring tasks             | `Task.mark_complete()`, `Task.next_occurrence()`   | Completing a `"daily"`/`"weekly"` task auto-spawns the next instance.   |
| Conflict handling (basic)   | `Scheduler.detect_conflicts()`                     | Lightweight: flags tasks sharing the exact same start time.             |
| Conflict handling (overlap) | `Scheduler.detect_overlaps()`                      | Stronger: flags overlapping time _ranges_ using start + duration.       |
| Conflict report             | `Scheduler.conflict_report()`                      | Returns a warning string (never raises); `check_overlaps` toggles mode. |
| Build & explain the plan    | `Scheduler.generate_plan()`, `Scheduler.explain()` | Produces the final ordered plan and a human-readable rationale.         |

### Feature details

- **Sorting.** `sort_tasks()` ranks by priority (`PRIORITY_RANK`) then duration;
  `sort_by_time()` uses a lambda key on the `"HH:MM"` string, which sorts
  chronologically because the values are zero-padded 24-hour times.
- **Filtering.** `filter_tasks(pet_name=..., completed=...)` skips any filter
  left as `None`, so it handles "all of Mochi's tasks", "all open tasks", or
  both at once. `filter_by_time()` is the time-budget greedy selector.
- **Recurring tasks.** `Task.recurrence` is `"none"`, `"daily"`, or `"weekly"`.
  When `mark_complete()` is called, `next_occurrence()` clones the task (via
  `dataclasses.replace`) with its `date` advanced by `RECURRENCE_DELTAS` and
  appends it to the same pet using the `Task.pet` back-reference.
- **Conflict detection.** `detect_conflicts()` is the lightweight same-start-time
  check; `detect_overlaps()` is the stronger interval check that also catches
  partial overlaps (e.g. an 18:15 task inside an 18:00–18:30 task). Both return
  warning strings and skip untimed/malformed entries rather than crashing.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
