"""Flask app — rubric comment viewer."""
from flask import Flask, render_template, jsonify, request, abort
import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent / "comments.db"
app = Flask(__name__)


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# ── API ──────────────────────────────────────────────────────────────────────

@app.get("/api/year-levels")
def year_levels():
    return jsonify(list(range(4, 13)))


@app.get("/api/tasks")
def tasks():
    year = request.args.get("year", type=int)
    with get_db() as con:
        if year:
            rows = con.execute(
                "SELECT id, name, year_level FROM tasks WHERE year_level=? ORDER BY name",
                (year,)
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT id, name, year_level FROM tasks ORDER BY year_level, name"
            ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/tasks/<int:task_id>/comments")
def task_comments(task_id):
    with get_db() as con:
        task = con.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not task:
            abort(404)
        criteria = con.execute(
            "SELECT * FROM rubric_criteria WHERE task_id=? ORDER BY sort_order, id",
            (task_id,)
        ).fetchall()
        result = {
            "task": dict(task),
            "criteria": []
        }
        for c in criteria:
            comments = con.execute(
                "SELECT achievement_level, comment_text FROM comments "
                "WHERE criteria_id=? ORDER BY achievement_level",
                (c["id"],)
            ).fetchall()
            result["criteria"].append({
                **dict(c),
                "comments": {row["achievement_level"]: row["comment_text"] for row in comments}
            })
    return jsonify(result)


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    from init_db import init
    init()
    app.run(debug=True, port=5000)
