"""PawPal+ core domain classes.

Defines the data objects (Owner, Pet, Task) and the Scheduler that turns
a list of tasks into a daily plan based on the owner's constraints.
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta


# Priority labels mapped to a sortable rank (lower number = scheduled first).
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# How far ahead the next occurrence of a recurring task lands.
RECURRENCE_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single care task to be scheduled."""

    title: str
    duration: int  # minutes
    priority: str = "medium"  # "high", "medium", or "low"
    completed: bool = False
    pet_name: str = ""  # set when the task is added to a Pet
    time: str = ""  # scheduled start time in "HH:MM" (24-hour) format
    recurrence: str = "none"  # "none", "daily", or "weekly"
    date: str = ""  # ISO "YYYY-MM-DD" day this instance is scheduled for
    pet: "Pet" = field(default=None, repr=False, compare=False)  # owning pet

    def priority_rank(self) -> int:
        """Return a sortable rank; unknown priorities sort last."""
        return PRIORITY_RANK.get(self.priority.lower(), len(PRIORITY_RANK))

    def next_occurrence(self) -> "Task":
        """Build the next instance of a recurring task, or None if one-off.

        Advances the date by one day ("daily") or one week ("weekly"). If this
        instance has no date, today is used as the starting point.
        """
        delta = RECURRENCE_DELTAS.get(self.recurrence.lower())
        if delta is None:
            return None
        base = date.fromisoformat(self.date) if self.date else date.today()
        # Clone this task, overriding only the day and resetting completion.
        return replace(self, date=(base + delta).isoformat(), completed=False)

    def mark_complete(self) -> "Task":
        """Mark this task done; auto-spawn the next occurrence if recurring.

        For "daily"/"weekly" tasks the new instance is appended to the same pet
        and returned. One-off tasks just complete and return None.
        """
        self.completed = True
        nxt = self.next_occurrence()
        if nxt is not None and self.pet is not None:
            self.pet.add_task(nxt)
        return nxt


@dataclass
class Pet:
    """A pet being cared for, along with its own care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, stamping it with the pet's name.

        Also stores a back-reference so the task can spawn its next occurrence
        onto this pet when it is completed.
        """
        task.pet_name = self.name
        task.pet = self
        self.tasks.append(task)

    def summary(self) -> str:
        return f"{self.name} ({self.species})"


@dataclass
class Owner:
    """The pet owner: manages multiple pets and their daily constraints."""

    name: str
    available_mins: int
    preferences: dict = field(default_factory=dict)
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list:
        """Flatten every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    """Builds a daily plan from an owner's tasks within their time budget."""

    owner: Owner

    def pending_tasks(self) -> list:
        """Retrieve all not-yet-completed tasks across the owner's pets."""
        return [t for t in self.owner.all_tasks() if not t.completed]

    def sort_tasks(self) -> list:
        """Return pending tasks ordered by priority, then shortest duration."""
        return sorted(self.pending_tasks(), key=lambda t: (t.priority_rank(), t.duration))

    def sort_by_time(self) -> list:
        """Return pending tasks ordered chronologically by start time.

        Times are "HH:MM" strings; zero-padded 24-hour values sort the same
        lexicographically as chronologically. Untimed tasks (empty string)
        sort last.
        """
        return sorted(self.pending_tasks(), key=lambda t: t.time or "99:99")

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list:
        """Return tasks matching the given completion status and/or pet name.

        Both filters are optional; leaving one as ``None`` ignores it. With no
        arguments this returns every task. Pet-name matching is case-insensitive.
        """
        tasks = self.owner.all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() ==
                     pet_name.lower()]
        return tasks

    def detect_conflicts(self) -> list:
        """Find pending tasks scheduled at the same start time.

        Lightweight strategy: group timed tasks by their "HH:MM" slot and flag
        any slot holding more than one task. Catches same-pet *and* cross-pet
        clashes. Untimed tasks (no "time") are ignored. Same day is assumed.

        Returns a list of human-readable warning strings (empty if all clear) —
        it never raises, so callers can show warnings without crashing.
        """
        by_time = {}
        for task in self.pending_tasks():
            if task.time:  # skip untimed tasks
                by_time.setdefault(task.time, []).append(task)

        warnings = []
        for slot in sorted(by_time):
            clashing = by_time[slot]
            if len(clashing) > 1:
                who = ", ".join(
                    f"{t.title} ({t.pet_name or 'unassigned'})" for t in clashing
                )
                warnings.append(f"⚠️ Conflict at {slot}: {who}")
        return warnings

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert a "HH:MM" string to minutes since midnight."""
        hours, _, minutes = hhmm.partition(":")
        return int(hours) * 60 + int(minutes)

    def detect_overlaps(self) -> list:
        """Find pending tasks whose time *ranges* overlap (stronger mode).

        Unlike detect_conflicts (same start time only), this uses each task's
        start ("HH:MM") plus its duration to flag partial overlaps too — e.g. a
        30-min task at 18:00 collides with one at 18:15. Catches same-pet and
        cross-pet clashes. Untimed tasks are ignored, and malformed times are
        skipped rather than raised, so this never crashes.

        Returns a list of human-readable warning strings (empty if all clear).
        """
        # Build (start, end, task) intervals for every timed task.
        intervals = []
        for task in self.pending_tasks():
            if not task.time:
                continue
            try:
                start = self._to_minutes(task.time)
            except ValueError:
                continue  # skip malformed times instead of crashing
            intervals.append((start, start + task.duration, task))

        intervals.sort(key=lambda iv: iv[0])

        warnings = []
        for i, (_, end_a, task_a) in enumerate(intervals):
            for start_b, end_b, task_b in intervals[i + 1:]:
                if start_b >= end_a:
                    break  # sorted by start: nothing later can overlap A
                warnings.append(
                    f"⚠️ Overlap: {task_a.title} ({task_a.pet_name or 'unassigned'}) "
                    f"{task_a.time}–{self._fmt(end_a)} vs "
                    f"{task_b.title} ({task_b.pet_name or 'unassigned'}) "
                    f"{task_b.time}–{self._fmt(end_b)}"
                )
        return warnings

    @staticmethod
    def _fmt(minutes: int) -> str:
        """Format minutes-since-midnight back into "HH:MM"."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def conflict_report(self, check_overlaps: bool = True) -> str:
        """Return a summary of scheduling conflicts.

        With check_overlaps=True (default) it uses the stronger interval-overlap
        detection; set it False for the lightweight same-start-time check only.
        """
        warnings = self.detect_overlaps() if check_overlaps else self.detect_conflicts()
        if not warnings:
            return "✅ No scheduling conflicts."
        return "\n".join([f"Found {len(warnings)} conflict(s):"] + warnings)

    def filter_by_time(self) -> list:
        """Greedily keep tasks that fit within the owner's available minutes."""
        remaining = self.owner.available_mins
        kept = []
        for task in self.sort_tasks():
            if task.duration <= remaining:
                kept.append(task)
                remaining -= task.duration
        return kept

    def generate_plan(self) -> list:
        """Return the final ordered list of tasks that fit in the day."""
        return self.filter_by_time()

    def explain(self) -> str:
        """Describe the plan and the reasoning behind what was scheduled."""
        plan = self.generate_plan()
        scheduled_ids = {id(t) for t in plan}
        used = sum(t.duration for t in plan)
        budget = self.owner.available_mins

        def describe(task: Task) -> str:
            who = f" for {task.pet_name}" if task.pet_name else ""
            return f"  - {task.title}{who} ({task.duration} min) [priority: {task.priority}]"

        lines = [
            f"Daily plan for {self.owner.name} ({used}/{budget} min used):"]
        lines += [describe(t) for t in plan] or ["  (no tasks scheduled)"]

        skipped = [t for t in self.sort_tasks() if id(t) not in scheduled_ids]
        if skipped:
            lines.append("Skipped — not enough time left:")
            lines += [describe(t) for t in skipped]

        lines.append(
            "Reasoning: tasks are ordered by priority (high first), then by "
            "shortest duration, and added until the time budget runs out."
        )
        return "\n".join(lines)
