"""PawPal+ core domain classes.

Defines the data objects (Owner, Pet, Task) and the Scheduler that turns
a list of tasks into a daily plan based on the owner's constraints.
"""

from dataclasses import dataclass, field


# Priority labels mapped to a sortable rank (lower number = scheduled first).
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    """Basic info about the pet being cared for."""

    name: str
    species: str

    def summary(self) -> str:
        return f"{self.name} ({self.species})"


@dataclass
class Task:
    """A single care task to be scheduled."""

    title: str
    duration: int  # minutes
    priority: str = "medium"  # "high", "medium", or "low"

    def priority_rank(self) -> int:
        """Return a sortable rank; unknown priorities sort last."""
        return PRIORITY_RANK.get(self.priority.lower(), len(PRIORITY_RANK))


@dataclass
class Owner:
    """The pet owner, including their daily constraints and preferences."""

    name: str
    available_mins: int
    preferences: dict = field(default_factory=dict)


@dataclass
class Scheduler:
    """Builds a daily plan from an owner's tasks within their time budget."""

    owner: Owner
    tasks: list = field(default_factory=list)

    def sort_tasks(self) -> list:
        """Return tasks ordered by priority, then by shortest duration."""
        return sorted(self.tasks, key=lambda t: (t.priority_rank(), t.duration))

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
