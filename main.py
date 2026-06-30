"""Demo script for PawPal+.

Builds an owner with a couple of pets and some care tasks, then exercises
the Scheduler's sorting and filtering methods, printing results to the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def show(label: str, tasks: list) -> None:
    """Print a labeled list of tasks, one per line."""
    print(f"\n{label}")
    print("-" * 40)
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        when = t.time or "--:--"
        day = t.date or "----------"
        status = "done" if t.completed else "open"
        recur = "" if t.recurrence == "none" else f" {{{t.recurrence}}}"
        print(f"  {day} {when}  {t.title:<16} {t.pet_name:<8} "
              f"[{t.priority}] ({status}){recur}")


def main() -> None:
    # Create the owner with a daily time budget (in minutes).
    owner = Owner(name="Sam", available_mins=60)

    # Create two pets.
    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    mittens = Pet(name="Mittens", species="Cat")

    # Add care tasks with times deliberately OUT OF ORDER so sorting has
    # something to do. Note the afternoon walk is added before the morning feed.
    biscuit.add_task(Task("Evening walk", duration=30,
                     priority="high", time="18:00"))
    biscuit.add_task(Task("Grooming", duration=20, priority="low", time="09:30",
                          recurrence="weekly", date="2026-06-30"))
    mittens.add_task(Task("Feeding", duration=10, priority="high", time="07:15",
                          recurrence="daily", date="2026-06-30"))
    mittens.add_task(Task("Litter cleanup", duration=15,
                     priority="medium", time="12:45"))
    # Same-start clash: lands at 18:00, same as Biscuit's evening walk (cross-pet).
    mittens.add_task(Task("Vet call", duration=10,
                     priority="high", time="18:00"))
    # Partial overlap: starts 18:15, inside the 18:00–18:30 evening walk window.
    # Same start-time detection would MISS this; overlap detection catches it.
    mittens.add_task(Task("Pill time", duration=5,
                     priority="medium", time="18:15"))

    # Completing a recurring task auto-creates its next occurrence.
    print("\nCompleting Feeding (daily) and Grooming (weekly)...")
    feeding_next = mittens.tasks[0].mark_complete()   # daily -> +1 day
    grooming_next = biscuit.tasks[1].mark_complete()  # weekly -> +7 days
    print(
        f"  Feeding spawned next: {feeding_next.title} on {feeding_next.date}")
    print(
        f"  Grooming spawned next: {grooming_next.title} on {grooming_next.date}")

    # Register the pets with the owner.
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    scheduler = Scheduler(owner)

    print("PawPal+ Demo")
    print("=" * 40)

    # Tasks in the order they were added (unsorted).
    show("All tasks (insertion order)", owner.all_tasks())

    # New sorting method: pending tasks ordered chronologically by time.
    show("Pending tasks sorted by time", scheduler.sort_by_time())

    # New filtering methods.
    show("Filter: Biscuit's tasks", scheduler.filter_tasks(pet_name="Biscuit"))
    show("Filter: completed tasks", scheduler.filter_tasks(completed=True))
    show("Filter: open tasks", scheduler.filter_tasks(completed=False))

    print("\nConflict check (lightweight: same start time)")
    print("-" * 40)
    print(scheduler.conflict_report(check_overlaps=False))

    print("\nConflict check (stronger: overlapping time ranges)")
    print("-" * 40)
    print(scheduler.conflict_report())

    print("\n" + "=" * 40)
    print(scheduler.explain())


if __name__ == "__main__":
    main()
