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

---

## 6. AI Strategy

**a. Which AI coding assistant features were most effective for building your scheduler?**

The most effective feature was **multi-file context** — being able to point the
assistant at `pawpal_system.py`, `app.py`, and the UML at the same time. Because
it could see the real `Scheduler` API, its suggestions used the methods I had
actually written (`sort_tasks()`, `detect_overlaps()`, `generate_plan()`) instead
of inventing new ones. Two other features mattered a lot:

- **Edit-then-verify loops.** After each change the assistant byte-compiled
  `app.py` and re-ran `python main.py`, so I caught problems immediately rather
  than discovering them later in the browser.
- **Generating docs from the real code.** It read the final implementation to
  produce the updated UML (`uml_final.mmd`) and to capture _actual_ CLI output
  for the README, rather than guessing — which kept the documentation honest.

**b. One AI suggestion you rejected or modified to keep your system design clean.**

When I asked it to show conflict warnings in the UI, the first version just dumped
every warning into a single `st.warning` with the strings joined together. I
rejected that and had it refactored into a small reusable `render_conflicts()`
helper that leads with a count, renders each clash as its own bullet, adds a
suggested fix, and shows `st.success` when there are none. That kept the conflict
presentation in **one place** used by both the task list and the schedule section,
instead of two slightly different inline blocks. I also turned down an early
suggestion to auto-resolve overlapping tasks: warning the owner and letting them
decide keeps the scheduler's responsibility narrow and predictable.

**c. How using separate chat sessions for different phases helped you stay organized.**

I kept phases in separate sessions — **design/UML**, **core scheduling logic**,
**Streamlit UI**, and **documentation**. Each session stayed focused on one
concern, so the assistant wasn't juggling unrelated context and was less likely to
"helpfully" edit code outside the phase I was working on. It also made it easy to
go back and find the reasoning behind a specific decision, because each
conversation mapped to one part of the system.

**d. What you learned about being the "lead architect" when collaborating with powerful AI tools.**

The AI is fast at producing plausible code, but it optimizes for "a reasonable
answer," not "the right answer for _this_ design." My job as lead architect was to
own the **constraints and the boundaries**: choosing greedy-by-priority over a
knapsack optimizer because explainability matters more than packing minutes,
deciding conflicts should warn rather than auto-fix, and insisting suggestions be
verified against tests and real `main.py` output before I accepted them. The
assistant accelerated the work, but the coherence of the design came from me
saying no to scope creep and keeping every change consistent with the original
responsibilities of `Task`, `Pet`, `Owner`, and `Scheduler`.
