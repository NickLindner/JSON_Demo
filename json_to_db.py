"""
Reads a superhero JSON file and writes normalized relational tables to a SQLite database.

Table structure:
  heroes        — one row per hero (scalar fields)
  powers        — lookup table of unique power names
  hero_powers   — join table linking heroes to their powers (many-to-many)
"""

import json
import sqlite3


def load_json(filepath: str) -> list[dict]:
    with open(filepath, "r") as f:
        return json.load(f)


def normalize(heroes: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (hero_rows, power_rows, hero_power_rows) ready for DB insertion."""
    hero_rows = []
    power_map: dict[str, int] = {}  # power_name -> power_id
    hero_power_rows = []

    for hero in heroes:
        hero_rows.append({
            "id":               hero["id"],
            "name":             hero["name"],
            "real_name":        hero.get("real_name"),
            "universe":         hero["universe"],
            "first_appearance": hero.get("first_appearance"),
        })

        for power_name in hero.get("powers", []):
            if power_name not in power_map:
                power_map[power_name] = len(power_map) + 1
            hero_power_rows.append({
                "hero_id":  hero["id"],
                "power_id": power_map[power_name],
            })

    power_rows = [{"id": pid, "name": name} for name, pid in power_map.items()]
    return hero_rows, power_rows, hero_power_rows


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS heroes (
            id               INTEGER PRIMARY KEY,
            name             TEXT    NOT NULL,
            real_name        TEXT,
            universe         TEXT    NOT NULL,
            first_appearance INTEGER
        );

        CREATE TABLE IF NOT EXISTS powers (
            id   INTEGER PRIMARY KEY,
            name TEXT    NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS hero_powers (
            hero_id  INTEGER NOT NULL REFERENCES heroes(id),
            power_id INTEGER NOT NULL REFERENCES powers(id),
            PRIMARY KEY (hero_id, power_id)
        );
    """)


def insert_data(
    conn: sqlite3.Connection,
    hero_rows: list[dict],
    power_rows: list[dict],
    hero_power_rows: list[dict],
) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO heroes (id, name, real_name, universe, first_appearance) "
        "VALUES (:id, :name, :real_name, :universe, :first_appearance)",
        hero_rows,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO powers (id, name) VALUES (:id, :name)",
        power_rows,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO hero_powers (hero_id, power_id) VALUES (:hero_id, :power_id)",
        hero_power_rows,
    )
    conn.commit()


def print_summary(conn: sqlite3.Connection) -> None:
    print("\n=== heroes ===")
    for row in conn.execute("SELECT * FROM heroes"):
        print(dict(row))

    print("\n=== powers ===")
    for row in conn.execute("SELECT * FROM powers ORDER BY id"):
        print(dict(row))

    print("\n=== hero_powers (joined) ===")
    query = """
        SELECT h.name AS hero, p.name AS power
        FROM hero_powers hp
        JOIN heroes h ON h.id = hp.hero_id
        JOIN powers p ON p.id = hp.power_id
        ORDER BY h.name, p.name
    """
    for row in conn.execute(query):
        print(dict(row))


def main():
    json_file = "superheroes.json"
    db_file   = "superheroes.db"

    heroes = load_json(json_file)
    hero_rows, power_rows, hero_power_rows = normalize(heroes)

    print(f"Loaded {len(hero_rows)} heroes, "
          f"{len(power_rows)} unique powers, "
          f"{len(hero_power_rows)} hero-power links")

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row

    create_tables(conn)
    insert_data(conn, hero_rows, power_rows, hero_power_rows)

    print(f"Data written to '{db_file}'")
    print_summary(conn)

    conn.close()


if __name__ == "__main__":
    main()
