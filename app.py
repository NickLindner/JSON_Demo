"""
Minimal Flask site demonstrating Jinja2 template inheritance.

All pages extend templates/base.html, which defines the shared
header, navigation, and footer.

Run with:
  pip install -r requirements.txt
  python app.py
"""

import json
from pathlib import Path

from flask import Flask, abort, render_template

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "superheroes.json"


def load_heroes() -> list[dict]:
    with open(DATA_FILE, "r") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/heroes")
def heroes():
    return render_template("heroes.html", heroes=load_heroes())


@app.route("/heroes/<int:hero_id>")
def hero_detail(hero_id: int):
    hero = next((h for h in load_heroes() if h["id"] == hero_id), None)
    if hero is None:
        abort(404)
    return render_template("hero.html", hero=hero)


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
