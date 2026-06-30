"""Tests for the PawPal+ domain classes."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    """Calling mark_complete() changes the task's status to completed."""
    task = Task("Feeding", duration=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Biscuit", "Golden Retriever")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Morning walk", duration=30, priority="high"))
    assert len(pet.tasks) == 1


def _scheduler_with(tasks):
    """Build a Scheduler whose single pet owns the given tasks."""
    pet = Pet("Biscuit", "Golden Retriever")
    for task in tasks:
        pet.add_task(task)
    owner = Owner("Alex", available_mins=240)
    owner.add_pet(pet)
    return Scheduler(owner)


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() orders pending tasks chronologically; untimed sort last."""
    scheduler = _scheduler_with([
        Task("Evening walk", duration=30, time="18:00"),
        Task("Breakfast", duration=10, time="07:30"),
        Task("Vet meds", duration=5),  # untimed -> should sort last
        Task("Lunch", duration=15, time="12:00"),
    ])

    ordered = scheduler.sort_by_time()
    titles = [t.title for t in ordered]

    assert titles == ["Breakfast", "Lunch", "Evening walk", "Vet meds"]


def test_daily_task_completion_spawns_next_day():
    """Completing a daily task creates a fresh task dated one day later."""
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Feeding", duration=10, recurrence="daily", date="2026-06-30")
    pet.add_task(task)
    assert len(pet.tasks) == 1

    nxt = task.mark_complete()

    # A new occurrence was appended to the same pet.
    assert len(pet.tasks) == 2
    assert nxt is not None
    # Dated the following day, reset to not-completed.
    expected = (date.fromisoformat("2026-06-30") + timedelta(days=1)).isoformat()
    assert nxt.date == expected
    assert nxt.completed is False
    # The original is now complete.
    assert task.completed is True


def test_detect_conflicts_flags_duplicate_times():
    """Two pending tasks sharing a start time are flagged as a conflict."""
    scheduler = _scheduler_with([
        Task("Walk", duration=30, time="08:00"),
        Task("Brush", duration=15, time="08:00"),  # same slot -> conflict
        Task("Nap", duration=20, time="14:00"),    # alone -> no conflict
    ])

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "14:00" not in warnings[0]
