import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "resources.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                description TEXT NOT NULL,
                url TEXT NOT NULL
            )"""
        )


def create_resource(data: dict) -> dict:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO resources (title, topic, description, url) VALUES (?, ?, ?, ?)",
            (data["title"], data["topic"], data["description"], data["url"]),
        )
        new_id = cur.lastrowid
    return get_resource(new_id)


def get_all_resources() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM resources ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def get_resource(resource_id: int):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM resources WHERE id = ?", (resource_id,)
        ).fetchone()
    return dict(row) if row else None


def update_resource(resource_id: int, data: dict):
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE resources SET title=?, topic=?, description=?, url=? WHERE id=?",
            (data["title"], data["topic"], data["description"], data["url"], resource_id),
        )
        if cur.rowcount == 0:
            return None
    return get_resource(resource_id)


def delete_resource(resource_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        return cur.rowcount > 0