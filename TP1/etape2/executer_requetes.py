# -*- coding: utf-8 -*-
"""Execute les 10 requetes stats et ecrit les resultats dans un fichier texte."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

ETAPE2 = Path(__file__).resolve().parent
DB = ETAPE2.parent / "q6" / "tp1_cible.db"
SQL_FILE = ETAPE2 / "01_requetes_stats.sql"
OUT = ETAPE2 / "02_requetes_resultats.txt"


def split_queries(sql: str) -> list[tuple[str, str]]:
    """Retourne [(titre, sql), ...] a partir des commentaires -- Qxx."""
    parts = re.split(r"(?m)^-- (Q\d+.*)$", sql)
    # parts: preamble, title1, body1, title2, body2, ...
    queries = []
    i = 1
    while i + 1 < len(parts):
        title = parts[i].strip()
        body = parts[i + 1]
        # remove trailing comments-only lines noise before next
        body = re.sub(r"(?m)^--.*$", "", body)
        body = body.strip().rstrip(";")
        if body:
            queries.append((title, body))
        i += 2
    return queries


def main() -> None:
    sql = SQL_FILE.read_text(encoding="utf-8")
    queries = split_queries(sql)
    conn = sqlite3.connect(DB)
    lines = [
        "TP1 - Etape 2 - 10 requetes SQL et exemples de resultats",
        "=" * 70,
        f"Base : {DB}",
        f"Nombre de requetes : {len(queries)}",
        "",
    ]
    print(f"{len(queries)} requetes sur {DB}")
    for title, q in queries:
        print(">", title)
        df = pd.read_sql_query(q, conn)
        lines.append("-" * 70)
        lines.append(title)
        lines.append("-" * 70)
        lines.append(q.strip() + ";")
        lines.append("")
        lines.append("Resultat :")
        if df.empty:
            lines.append("(aucun resultat)")
        else:
            lines.append(df.to_string(index=False))
        lines.append("")
        lines.append(f"[{len(df)} ligne(s)]")
        lines.append("")
    conn.close()
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Ecrit:", OUT)


if __name__ == "__main__":
    main()
