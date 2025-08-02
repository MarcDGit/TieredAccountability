import streamlit as st
from datetime import datetime, timedelta
from db import init_db, get_all_people, get_all_tiers, add_tier, add_person, add_task, fetch_tasks_for_person, update_task_status

# ---------------------------------------------------------------------------
# Initial setup & helpers
# ---------------------------------------------------------------------------

init_db()

URGENCY_LEVELS = ["Low", "Medium", "High"]


def _filter_tasks(tasks, urgency_filter, max_days_open):
    """Return a filtered list of tasks according to urgency and age."""
    filtered = []
    now = datetime.utcnow()
    for t in tasks:
        age_days = (now - datetime.fromisoformat(t["created_at"]).replace(tzinfo=None)).days
        if urgency_filter and t["urgency"] not in urgency_filter:
            continue
        if age_days > max_days_open:
            continue
        filtered.append(t)
    return filtered


def _tier_choices():
    tiers = get_all_tiers()
    return {f"{t['name']} (ID {t['id']})": t["id"] for t in tiers}


def _person_choices():
    people = get_all_people()
    return {f"{p['name']} (Tier {p['tier_name']})": p["id"] for p in people}


# ---------------------------------------------------------------------------
# Session: Login (simple user switcher)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Tiered Accountability Dashboard", layout="wide")

if "person_id" not in st.session_state:
    st.session_state.person_id = None

if st.session_state.person_id is None:
    st.title("🔐 Login")
    persons = _person_choices()
    person_select = st.selectbox("Bitte Person wählen (oder neue Person unten anlegen):", list(persons.keys()) if persons else [])

    if st.button("Login") and person_select:
        st.session_state.person_id = persons[person_select]
        st.experimental_rerun()

    st.subheader("Neue Person anlegen")
    with st.form("add_person_form"):
        new_name = st.text_input("Name")
        tier_map = _tier_choices()
        new_tier_label = st.selectbox("Tier", list(tier_map.keys()) if tier_map else [])
        submitted = st.form_submit_button("Person erstellen")
        if submitted and new_name and new_tier_label:
            add_person(new_name, tier_map[new_tier_label])
            st.success("Person angelegt. Bitte nun zum Login oben zurückkehren.")

    st.stop()

# After login --------------------------------------------------------------

person_id = st.session_state.person_id
people_dict = {p["id"]: p for p in get_all_people()}
current_user = people_dict[person_id]

st.sidebar.header(f"👤 {current_user['name']}")

selection = st.sidebar.radio("Navigation", ["Dashboard", "Neue Eskalation", "Admin Panel", "Logout"])

if selection == "Logout":
    st.session_state.person_id = None
    st.experimental_rerun()

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

if selection == "Dashboard":
    st.title("📊 Mein Dashboard")
    tasks = fetch_tasks_for_person(person_id)

    # Filters
    st.subheader("Filter")
    col1, col2 = st.columns(2)
    with col1:
        urg_filter = st.multiselect("Urgency", URGENCY_LEVELS, default=URGENCY_LEVELS)
    with col2:
        max_days = st.slider("Max Tage offen", 0, 60, 60)

    filtered_tasks = _filter_tasks(tasks, urg_filter, max_days)

    # Split into categories
    to_me = [t for t in filtered_tasks if t["assigned_to"] == person_id and t["status"] != "closed"]
    from_me = [t for t in filtered_tasks if t["created_by"] == person_id]

    st.subheader("📝 Aufgaben an mich")
    for t in to_me:
        with st.expander(f"#{t['id']} | {t['title']} | {t['urgency']} | Status: {t['status']}"):
            st.markdown(f"**Beschreibung:** {t['description']}")
            st.markdown(f"**Von:** {t['creator_name']} (Tier {t['tier_from_name']})")
            st.markdown(f"**Seit:** {t['created_at']}")
            if t["status"] == "escalated":
                if st.button("Als erledigt markieren", key=f"resolve_{t['id']}"):
                    update_task_status(t["id"], "resolved")
                    st.experimental_rerun()

    st.subheader("📤 Meine Eskalationen")
    for t in from_me:
        with st.expander(f"#{t['id']} | {t['title']} | {t['urgency']} | Status: {t['status']}"):
            st.markdown(f"**Zugewiesen an:** {t['assigned_to_name']} (Tier {t['tier_to_name']})")
            st.markdown(f"**Seit:** {t['created_at']}")
            if t["status"] == "resolved":
                st.success("Eskalation bearbeitet – bitte schließen, wenn OK")
                if st.button("Schließen", key=f"close_{t['id']}"):
                    update_task_status(t["id"], "closed")
                    st.experimental_rerun()
            elif t["status"] == "closed":
                st.info("Abgeschlossen ✔️")

# ---------------------------------------------------------------------------
# Neue Eskalation
# ---------------------------------------------------------------------------

elif selection == "Neue Eskalation":
    st.title("🚀 Neue Eskalation anlegen")

    my_tier_id = current_user["tier_id"]
    tiers = {t["id"]: t for t in get_all_tiers()}
    parent_tier_id = tiers[my_tier_id]["parent_id"] if my_tier_id in tiers else None

    if parent_tier_id is None:
        st.warning("Für Ihr Tier existiert keine übergeordnete Ebene – Eskalation nicht möglich.")
        st.stop()

    # Persons in parent tier
    candidates = [p for p in get_all_people() if p["tier_id"] == parent_tier_id]
    if not candidates:
        st.warning("Keine Personen im übergeordneten Tier vorhanden. Bitte Admin kontaktieren.")
        st.stop()

    person_options = {f"{p['name']} (ID {p['id']})": p["id"] for p in candidates}

    with st.form("escalate_form"):
        title = st.text_input("Titel der Aufgabe")
        desc = st.text_area("Beschreibung")
        assigned_label = st.selectbox("Zuständig (Tier+1)", list(person_options.keys()))
        urgency = st.selectbox("Dringlichkeit", URGENCY_LEVELS, index=1)
        submitted = st.form_submit_button("Eskalieren")

        if submitted and title and assigned_label:
            add_task(
                title=title,
                description=desc,
                created_by=person_id,
                tier_from=my_tier_id,
                tier_to=parent_tier_id,
                assigned_to=person_options[assigned_label],
                urgency=urgency,
            )
            st.success("Eskalation angelegt!")

# ---------------------------------------------------------------------------
# Admin Panel
# ---------------------------------------------------------------------------

elif selection == "Admin Panel":
    st.title("⚙️ Admin Panel")

    st.subheader("Tiers verwalten")
    tiers = get_all_tiers()
    st.table([{"ID": t["id"], "Name": t["name"], "Parent": t["parent_id"]} for t in tiers])

    with st.form("add_tier_form"):
        new_tier_name = st.text_input("Neues Tier Name")
        parent_options = {"—": None}
        parent_options.update({t["name"]: t["id"] for t in tiers})
        parent_label = st.selectbox("Parent Tier", list(parent_options.keys()))
        submitted_tier = st.form_submit_button("Tier erstellen")
        if submitted_tier and new_tier_name:
            add_tier(new_tier_name, parent_options[parent_label])
            st.success("Tier erstellt ✅")
            st.experimental_rerun()

    st.subheader("Personen verwalten")
    ppl = get_all_people()
    st.table(
        [
            {
                "ID": p["id"],
                "Name": p["name"],
                "Tier": p["tier_name"],
            }
            for p in ppl
        ]
    )

    with st.form("add_person_admin"):
        person_name = st.text_input("Name")
        tier_map = _tier_choices()
        tier_label = st.selectbox("Tier", list(tier_map.keys()))
        submitted_p = st.form_submit_button("Person hinzufügen")
        if submitted_p and person_name:
            add_person(person_name, tier_map[tier_label])
            st.success("Person hinzugefügt ✅")
            st.experimental_rerun()