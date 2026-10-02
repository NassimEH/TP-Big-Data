# -*- coding: utf-8 -*-
"""
TP1 - Question 3
Genere / execute le schema relationnel SQL (issu du MCD) dans SQLite.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

Q3_DIR = Path(__file__).resolve().parent
SQL_PATH = Q3_DIR / "01_schema_cible.sql"
DB_PATH = Q3_DIR / "tp1_cible.db"


def main() -> None:
    sql = SQL_PATH.read_text(encoding="utf-8")
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        print("Base creee :", DB_PATH)
        print("Tables :")
        for (name,) in tables:
            n = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            print(f"  - {name:<16} {n} lignes (vide = OK pour Q3)")
    finally:
        conn.close()

    print("\nOuvrir dans SQLiteStudio :")
    print(f"  {DB_PATH}")
    print(f"Script SQL : {SQL_PATH}")


if __name__ == "__main__":
    main()
