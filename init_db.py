"""Initialise (or reset) the SQLite database from schema.sql."""
import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent / "comments.db"
SCHEMA  = pathlib.Path(__file__).parent / "schema.sql"

def init():
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text())
    con.commit()
    con.close()
    print(f"Database ready: {DB_PATH}")

if __name__ == "__main__":
    init()
