# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

* we need a Pet class to be able to create for each pet
* check what the pet needs done (tasks like walks, feeding, meds, enrichment, grooming, etc.)
* do tasks depending on priority, time availability, owner preferences

4 Classes - Owner / Pet / Tasks / Scheduler

class Owner:
name:
available_mins:
preferences:

class Pet:
name:
species:

class Task:
title:
duration:
priority

class Scheduler

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff: greedy, priority-first task selection instead of an optimal fit.**

`Scheduler.filter_by_time()` sorts pending tasks by priority (then shortest
duration) and adds them one by one until the owner's `available_mins` runs out.
It is a _greedy_ algorithm: it commits to the highest-priority tasks first and
never reconsiders. This means it can leave time on the table — for example, with
a 60-minute budget and tasks of 50 (high), 30 (medium), and 30 (medium) minutes,
it schedules only the 50-minute task and wastes 10 minutes, even though the two
30-minute tasks would have filled the day exactly. A true optimizer (0/1 knapsack)
would pack the time more tightly.

I chose greedy anyway because it is reasonable for this scenario:

- **It honors what the owner actually cares about.** For pet care, doing the
  _important_ tasks (meds, feeding) matters more than squeezing maximum minutes
  out of the day. A knapsack that maximizes time used could drop a high-priority
  task to fit two low-priority ones — the wrong call for a pet.
- **It is simple, fast, and predictable.** `O(n log n)` for the sort vs. the
  added complexity of a DP table, for a list that is only ever a handful of tasks.
- **It is explainable.** `explain()` can state a clear rule ("highest priority
  first, until time runs out"), which an owner can trust and predict.

A related tradeoff: conflict detection only _warns_ (`detect_overlaps()` returns
messages) rather than auto-resolving clashes. The owner stays in control and
decides what to move, instead of the app silently dropping or rescheduling a task.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
