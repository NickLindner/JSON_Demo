"""Add a sample task with rubric criteria (no comments yet) so the UI can be tested."""
import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent / "comments.db"

SAMPLE = {
    "name": "Sample Writing Task",
    "year_level": 7,
    "description": "An extended writing response",
    "criteria": [
        {"name": "Ideas & Content",      "description": "Quality and development of ideas"},
        {"name": "Structure & Organisation", "description": "Logical flow and paragraph structure"},
        {"name": "Language & Vocabulary",   "description": "Word choice and language conventions"},
        {"name": "Spelling & Punctuation",  "description": "Accuracy of mechanical conventions"},
    ]
}

def seed():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.execute(
        "INSERT OR IGNORE INTO tasks (name, year_level, description) VALUES (?,?,?)",
        (SAMPLE["name"], SAMPLE["year_level"], SAMPLE["description"])
    )
    task_id = cur.lastrowid or con.execute(
        "SELECT id FROM tasks WHERE name=? AND year_level=?",
        (SAMPLE["name"], SAMPLE["year_level"])
    ).fetchone()[0]

    for i, c in enumerate(SAMPLE["criteria"]):
        con.execute(
            "INSERT OR IGNORE INTO rubric_criteria (task_id, name, description, sort_order) VALUES (?,?,?,?)",
            (task_id, c["name"], c["description"], i)
        )
    con.commit()
    con.close()
    print("Sample task seeded.")

if __name__ == "__main__":
    seed()
