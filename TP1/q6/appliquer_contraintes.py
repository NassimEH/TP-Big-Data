# -*- coding: utf-8 -*-
"""
TP1 - Question 6
Applique les contraintes d'integrite (PK/FK/domaine) sur une copie de la base
chargee en Q5, puis prouve qu'elles sont actives.
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

Q6_DIR = Path(__file__).resolve().parent
TP1_DIR = Q6_DIR.parent
SRC_DB = TP1_DIR / "q5" / "tp1_cible.db"
DST_DB = Q6_DIR / "tp1_cible.db"
SCHEMA = Q6_DIR / "01_contraintes_integrite.sql"
PROOF = Q6_DIR / "02_preuve_contraintes.txt"

TABLES = [
    "Medicaments",
    "Patients",
    "Presentations",
    "Substances",
    "Groupes",
    "Laboratoires",
    "Prendre",
    "Composer",
    "Appartenir",
    "Detenir",
]


def migrate() -> sqlite3.Connection:
    if not SRC_DB.exists():
        raise FileNotFoundError(f"Base Q5 introuvable : {SRC_DB}")

    if DST_DB.exists():
        DST_DB.unlink()

    # 1) creer schema cible avec contraintes
    conn = sqlite3.connect(DST_DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    # 2) attacher la base Q5 et copier les donnees
    conn.execute(f"ATTACH DATABASE ? AS src", (str(SRC_DB),))
    for t in TABLES:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')]
        col_list = ", ".join(f'"{c}"' for c in cols)
        conn.execute(
            f'INSERT INTO main."{t}" ({col_list}) SELECT {col_list} FROM src."{t}"'
        )
        n = conn.execute(f'SELECT COUNT(*) FROM main."{t}"').fetchone()[0]
        print(f"migre {t:<16} {n:,}")
    conn.commit()
    conn.execute("DETACH DATABASE src")
    return conn


def prove(conn: sqlite3.Connection) -> None:
    lines: list[str] = []
    lines.append("TP1 - Question 6 - Preuve des contraintes d'integrite")
    lines.append("=" * 60)
    lines.append(f"Base : {DST_DB.resolve()}")
    lines.append("")

    # PK / FK inventaire
    lines.append("1) Cles primaires (PRAGMA table_info / pk)")
    for t in TABLES:
        pks = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")') if r[5]]
        lines.append(f"   - {t}: PK = ({', '.join(pks)})")

    lines.append("")
    lines.append("2) Cles etrangeres (PRAGMA foreign_key_list)")
    for t in TABLES:
        fks = conn.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
        if not fks:
            continue
        for fk in fks:
            # id, seq, table, from, to, on_update, on_delete, match
            lines.append(f"   - {t}.{fk[3]} -> {fk[2]}({fk[4]})")

    lines.append("")
    lines.append("3) Contraintes de domaine (CHECK) - tests d'insertion refusee")

    tests = [
        (
            "Patients.age hors domaine (150)",
            "INSERT INTO Patients VALUES ('XBAD', 'A', 'B', 150, 'Male', 'a@b.c')",
        ),
        (
            "Patients.genre invalide",
            "INSERT INTO Patients VALUES ('XBAD2', 'A', 'B', 20, 'Alien', 'a@b.c')",
        ),
        (
            "Prendre.posologie > 5",
            "UPDATE Prendre SET posologie = 9 WHERE rowid = (SELECT rowid FROM Prendre LIMIT 1)",
        ),
        (
            "Prendre.duree > 30",
            "UPDATE Prendre SET duree = 99 WHERE rowid = (SELECT rowid FROM Prendre LIMIT 1)",
        ),
        (
            "Prendre.datePrise < 2025-01-01",
            "UPDATE Prendre SET datePrise = '2024-12-31' WHERE rowid = (SELECT rowid FROM Prendre LIMIT 1)",
        ),
        (
            "Appartenir.typeGenerique invalide (3)",
            "UPDATE Appartenir SET typeGenerique = 3 WHERE rowid = (SELECT rowid FROM Appartenir LIMIT 1)",
        ),
        (
            "Presentations.prixMedic negatif",
            "UPDATE Presentations SET prixMedic = -1 WHERE rowid = (SELECT rowid FROM Presentations LIMIT 1)",
        ),
        (
            "FK Presentations.idfMedic inexistant",
            """
            INSERT INTO Presentations
            VALUES ('8888888', 'orphan', NULL, NULL, NULL, 1.0, 1.0, -999999)
            """,
        ),
    ]

    conn.execute("PRAGMA foreign_keys = ON")
    print("\nTests refus (attendu = CONSTRAINT failed) :")
    for titre, sql in tests:
        try:
            conn.execute(sql)
            conn.commit()
            result = "ECHEC DU TEST (insertion acceptee a tort)"
        except sqlite3.IntegrityError as e:
            conn.rollback()
            result = f"REFUSE OK ({e})"
        lines.append(f"   - {titre}")
        lines.append(f"       -> {result}")
        print(f"  {titre}: {result}")

    lines.append("")
    lines.append("4) Effectifs apres migration (inchanges vs Q5)")
    for t in TABLES:
        n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        lines.append(f"   - {t}: {n}")

    PROOF.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nPreuve : {PROOF}")


def main() -> None:
    print("Migration Q6 (contraintes) ...")
    conn = migrate()
    try:
        prove(conn)
    finally:
        conn.close()
    print("\nBase finale :", DST_DB)


if __name__ == "__main__":
    main()
