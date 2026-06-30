"""Tests for the PawPal+ domain classes."""

from pawpal_system import Pet, Task


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
