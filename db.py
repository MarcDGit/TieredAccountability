import sqlite3
from pathlib import Path
from datetime import datetime

_DB_PATH = Path(__file__).parent / "data.db"


def _get_connection() -> sqlite3.Connection:
    """Return a thread-safe connection to the SQLite database with row mapping enabled."""
    conn = sqlite3.connect(_DB_PATH.as_posix(), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def init_db() -> None:
    """Create all tables if they do not already exist."""
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tiers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL UNIQUE,
            parent_id  INTEGER REFERENCES tiers(id) ON DELETE SET NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            tier_id  INTEGER NOT NULL REFERENCES tiers(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            description  TEXT,
            created_by   INTEGER NOT NULL REFERENCES people(id)   ON DELETE CASCADE,
            tier_from    INTEGER NOT NULL REFERENCES tiers(id)    ON DELETE CASCADE,
            tier_to      INTEGER NOT NULL REFERENCES tiers(id)    ON DELETE CASCADE,
            assigned_to  INTEGER NOT NULL REFERENCES people(id)   ON DELETE CASCADE,
            urgency      TEXT    NOT NULL DEFAULT 'Medium',
            status       TEXT    NOT NULL DEFAULT 'escalated',
            created_at   TEXT    NOT NULL,
            resolved_at  TEXT,
            closed_at    TEXT
        )
        """
    )

    conn.commit()

    # Ensure mindestens eine Tier-Ebene existiert, um erste Personen anlegen zu können
    if cur.execute("SELECT COUNT(*) FROM tiers").fetchone()[0] == 0:
        cur.execute("INSERT INTO tiers(name, parent_id) VALUES(?, NULL)", ("Tier 1",))
        conn.commit()
    conn.close()


# Utility helpers -----------------------------------------------------------

def get_all_tiers():
    conn = _get_connection()
    tiers = conn.execute("SELECT * FROM tiers ORDER BY id").fetchall()
    conn.close()
    return tiers


def get_all_people():
    conn = _get_connection()
    people = conn.execute(
        """
        SELECT p.*, t.name as tier_name
        FROM people p
        LEFT JOIN tiers t ON t.id = p.tier_id
        ORDER BY p.id
        """
    ).fetchall()
    conn.close()
    return people


def add_tier(name: str, parent_id: int | None):
    conn = _get_connection()
    conn.execute("INSERT INTO tiers(name, parent_id) VALUES(?, ?)", (name, parent_id))
    conn.commit()
    conn.close()


def add_person(name: str, tier_id: int):
    conn = _get_connection()
    conn.execute("INSERT INTO people(name, tier_id) VALUES(?, ?)", (name, tier_id))
    conn.commit()
    conn.close()


def add_task(title: str, description: str, created_by: int, tier_from: int, tier_to: int, assigned_to: int, urgency: str):
    now = datetime.utcnow().isoformat()
    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO tasks(title, description, created_by, tier_from, tier_to, assigned_to, urgency, status, created_at)
        VALUES(?,?,?,?,?,?,?, 'escalated', ?)
        """,
        (title, description, created_by, tier_from, tier_to, assigned_to, urgency, now),
    )
    conn.commit()
    conn.close()


def update_task_status(task_id: int, status: str):
    now = datetime.utcnow().isoformat()
    field = {
        'resolved': 'resolved_at',
        'closed': 'closed_at'
    }.get(status)

    conn = _get_connection()
    if field:
        conn.execute(
            f"UPDATE tasks SET status = ?, {field} = ? WHERE id = ?",
            (status, now, task_id),
        )
    else:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


def fetch_tasks_for_person(person_id: int):
    conn = _get_connection()
    tasks = conn.execute(
        """
        SELECT tasks.*, p.name as assigned_to_name, c.name as creator_name, t_from.name as tier_from_name, t_to.name as tier_to_name
        FROM tasks
        LEFT JOIN people p ON p.id = tasks.assigned_to
        LEFT JOIN people c ON c.id = tasks.created_by
        LEFT JOIN tiers t_from ON t_from.id = tasks.tier_from
        LEFT JOIN tiers t_to ON t_to.id = tasks.tier_to
        WHERE tasks.assigned_to = ? OR tasks.created_by = ?
        ORDER BY tasks.created_at DESC
        """,
        (person_id, person_id),
    ).fetchall()
    conn.close()
    return tasks