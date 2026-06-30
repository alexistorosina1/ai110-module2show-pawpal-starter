from datetime import time as dtime

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def render_conflicts(conflicts):
    """Present scheduler conflict warnings in a pet-owner-friendly way.

    Conflicts are advisories, not errors, so we use st.warning (amber) and lead
    with a count, itemize each clash as its own line, and end with a suggested
    fix. When nothing clashes we give positive confirmation via st.success.
    """
    if not conflicts:
        st.success("✅ No scheduling conflicts — your pet's day is all set!")
        return
    count = len(conflicts)
    label = "conflict" if count == 1 else "conflicts"
    # Strip the leading marker so we can render clean markdown bullets.
    bullets = "\n".join(f"- {c.lstrip('⚠️ ').strip()}" for c in conflicts)
    st.warning(
        f"**Heads up — {count} scheduling {label} found**\n\n"
        f"{bullets}\n\n"
        "💡 These tasks overlap in time. Consider rescheduling one of them "
        "so your pet isn't double-booked."
    )


st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
available_mins = st.number_input(
    "Available minutes today", min_value=0, max_value=1440, value=120
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Create the Owner and Pet once and keep them in the session vault so they
# survive Streamlit's reruns; only then sync them with the current UI values.
if "owner" not in st.session_state:
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, available_mins=int(available_mins))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet

owner = st.session_state.owner
pet = st.session_state.pet

# Keep the persisted objects in step with whatever is currently typed in.
owner.name = owner_name
owner.available_mins = int(available_mins)
pet.name = pet_name
pet.species = species

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into your scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    start_time = st.time_input("Start time", value=dtime(8, 0))

if st.button("Add task"):
    pet.add_task(Task(
        title=task_title,
        duration=int(duration),
        priority=priority,
        time=start_time.strftime("%H:%M"),
    ))

if pet.tasks:
    scheduler = Scheduler(owner)

    st.write(f"Current tasks for {pet.summary()}:")
    sort_choice = st.radio(
        "Sort tasks by",
        ["Priority", "Start time"],
        horizontal=True,
    )
    # Let the Scheduler decide the order rather than using insertion order.
    ordered = (
        scheduler.sort_tasks()
        if sort_choice == "Priority"
        else scheduler.sort_by_time()
    )

    # At-a-glance summary so the owner sees workload vs. budget instantly.
    pending = scheduler.pending_tasks()
    planned_mins = sum(t.duration for t in pending)
    m1, m2, m3 = st.columns(3)
    m1.metric("Pending tasks", len(pending))
    m2.metric("Time needed", f"{planned_mins} min")
    m3.metric("Daily budget", f"{owner.available_mins} min")

    st.table(
        [
            {
                "title": t.title,
                "pet": t.pet_name or "—",
                "time": t.time or "—",
                "duration_minutes": t.duration,
                "priority": t.priority,
                "completed": t.completed,
            }
            for t in ordered
        ]
    )

    # Lightweight conflict check: warn (don't crash) on overlapping tasks.
    render_conflicts(scheduler.detect_overlaps())
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption(
    "Runs the Scheduler over the tasks above, within the available time budget.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    if plan:
        used = sum(t.duration for t in plan)
        st.success(
            f"✅ Scheduled {len(plan)} task(s) — "
            f"{used} of {owner.available_mins} min used."
        )
        st.table(
            [
                {
                    "title": t.title,
                    "pet": t.pet_name,
                    "duration_minutes": t.duration,
                    "priority": t.priority,
                }
                for t in plan
            ]
        )
    else:
        st.warning(
            "No tasks fit in the available time. Add tasks or raise the budget.")

    # Surface time-overlap warnings using the shared, owner-friendly renderer.
    render_conflicts(scheduler.detect_overlaps())

    st.markdown("#### Explanation")
    st.text(scheduler.explain())
