# -*- coding: utf-8 -*-
"""
TP1 - Question 1
Etudier les donnees fournies (Python), les charger dans SQLite,
puis verifier la coherence entre tables via SQL.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

# q1/ -> TP1/data (donnees partagees) ; base SQLite locale a q1/
Q1_DIR = Path(__file__).resolve().parent
TP1_DIR = Q1_DIR.parent
DATA_DIR = TP1_DIR / "data"
DB_PATH = Q1_DIR / "tp1_initial.db"

# Schema source (fichiers bruts) - pas d'en-tete dans les .txt BDPM
COLS = {
    "CIS_bdpm": [
        "code_cis",
        "denomination",
        "forme",
        "voies_admin",
        "statut_amm",
        "type_procedure",
        "etat_commercialisation",
        "date_amm",
        "statut_bdm",
        "numero_autorisation_eu",
        "titulaires",
        "surveillance_renforcee",
    ],
    "CIS_CIP_bdpm": [
        "code_cis",
        "code_cip7",
        "libelle",
        "statut_admin",
        "etat_commercialisation",
        "date_declaration_com",
        "code_cip13",
        "agrement_collectivites",
        "taux_remboursement",
        "prix_medicament",
        "prix_public",
        "honoraires",
        "indications_remboursement",
    ],
    "CIS_COMPO_bdpm": [
        "code_cis",
        "element_pharmaceutique",
        "code_substance",
        "denomination_substance",
        "dosage",
        "reference_dosage",
        "nature_composant",
        "numero_lien",
    ],
    "CIS_GENER_bdpm": [
        "id_groupe",
        "libelle_groupe",
        "code_cis",
        "type_generique",
        "numero_tri",
    ],
}


def sep(msg: str) -> None:
    print("\n" + "=" * 72)
    print(msg)
    print("=" * 72)


def load_sources() -> dict[str, pd.DataFrame]:
    """Charge les fichiers sources avec les bons encodages / separateurs."""
    frames: dict[str, pd.DataFrame] = {}

    frames["CIS_bdpm"] = pd.read_csv(
        DATA_DIR / "CIS_bdpm.txt",
        sep="\t",
        header=None,
        names=COLS["CIS_bdpm"],
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )

    frames["CIS_CIP_bdpm"] = pd.read_csv(
        DATA_DIR / "CIS_CIP_bdpm.txt",
        sep="\t",
        header=None,
        names=COLS["CIS_CIP_bdpm"],
        dtype=str,
        encoding="utf-8",
        keep_default_na=False,
    )

    frames["CIS_COMPO_bdpm"] = pd.read_csv(
        DATA_DIR / "CIS_COMPO_bdpm.txt",
        sep="\t",
        header=None,
        names=COLS["CIS_COMPO_bdpm"],
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )

    frames["CIS_GENER_bdpm"] = pd.read_csv(
        DATA_DIR / "CIS_GENER_bdpm.txt",
        sep="\t",
        header=None,
        names=COLS["CIS_GENER_bdpm"],
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )

    # Sujet annonce ';' ; le fichier fourni utilise ','
    frames["healthcare"] = pd.read_csv(
        DATA_DIR / "healthcare_data.csv",
        sep=",",
        dtype=str,
        encoding="utf-8",
        keep_default_na=False,
    )

    return frames


def etudier(frames: dict[str, pd.DataFrame]) -> None:
    sep("1. ETUDE DES DONNEES FOURNIES")

    for name, df in frames.items():
        print(f"\n--- {name} ---")
        print(f"Lignes : {len(df):,} | Colonnes : {len(df.columns)}")
        print(f"Colonnes : {list(df.columns)}")
        vides = (df == "").sum()
        vides = vides[vides > 0]
        if len(vides):
            print("Champs vides (top) :")
            print(vides.sort_values(ascending=False).head(8).to_string())
        else:
            print("Aucun champ vide.")
        print("Apercu :")
        print(df.head(2).to_string(index=False))

    cis = frames["CIS_bdpm"]
    cip = frames["CIS_CIP_bdpm"]
    compo = frames["CIS_COMPO_bdpm"]
    gener = frames["CIS_GENER_bdpm"]
    patients = frames["healthcare"]

    sep("1.bis Particularites (attributs multivalues / redondances)")

    multi_voies = cis["voies_admin"].str.contains(";", regex=False).sum()
    multi_tit = cis["titulaires"].str.contains(";", regex=False).sum()
    multi_taux = cip["taux_remboursement"].str.contains(";", regex=False).sum()
    print(f"CIS avec plusieurs voies d'admin (';') : {multi_voies:,}")
    print(f"CIS avec plusieurs titulaires (';')     : {multi_tit:,}")
    print(f"CIP avec plusieurs taux rembt (';')     : {multi_taux:,}")

    print(
        f"CIS_COMPO : {len(compo):,} lignes pour "
        f"{compo['code_cis'].nunique():,} CIS distincts "
        f"(redondance -> plusieurs substances / elements)"
    )
    print(
        f"CIS_GENER : {len(gener):,} lignes pour "
        f"{gener['id_groupe'].nunique():,} groupes et "
        f"{gener['code_cis'].nunique():,} CIS "
        f"(redondance -> un groupe contient plusieurs medicaments)"
    )

    print("\nPatients - repartition genre / age :")
    print(patients["gender"].value_counts().to_string())
    ages = pd.to_numeric(patients["age"], errors="coerce")
    print(
        f"Age : min={ages.min()}, max={ages.max()}, "
        f"moyenne={ages.mean():.1f}, NaN={ages.isna().sum()}"
    )


def charger_sqlite(frames: dict[str, pd.DataFrame]) -> sqlite3.Connection:
    sep("2. CHARGEMENT DANS SQLITE")
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    mapping = {
        "CIS_bdpm": "cis_bdpm",
        "CIS_CIP_bdpm": "cis_cip_bdpm",
        "CIS_COMPO_bdpm": "cis_compo_bdpm",
        "CIS_GENER_bdpm": "cis_gener_bdpm",
        "healthcare": "healthcare",
    }
    for src, table in mapping.items():
        frames[src].to_sql(table, conn, index=False, if_exists="replace")
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"Table {table:<18} -> {n:,} lignes")

    print(f"\nBase creee : {DB_PATH}")
    return conn


def coherence_sql(conn: sqlite3.Connection) -> None:
    sep("3. COHERENCE DES DONNEES (SQL)")

    # Index pour accelerer les jointures / anti-jointures
    for sql_idx in [
        "CREATE INDEX IF NOT EXISTS idx_cis_code ON cis_bdpm(code_cis)",
        "CREATE INDEX IF NOT EXISTS idx_cip_cis ON cis_cip_bdpm(code_cis)",
        "CREATE INDEX IF NOT EXISTS idx_cip_cip7 ON cis_cip_bdpm(code_cip7)",
        "CREATE INDEX IF NOT EXISTS idx_compo_cis ON cis_compo_bdpm(code_cis)",
        "CREATE INDEX IF NOT EXISTS idx_gener_cis ON cis_gener_bdpm(code_cis)",
    ]:
        conn.execute(sql_idx)
    conn.commit()

    queries = [
        (
            "Medicaments SANS aucune presentation (CIP)",
            """
            SELECT COUNT(*) AS nb
            FROM cis_bdpm m
            LEFT JOIN (SELECT DISTINCT code_cis FROM cis_cip_bdpm) p
              ON m.code_cis = p.code_cis
            WHERE p.code_cis IS NULL
            """,
        ),
        (
            "Presentations dont le CIS est absent de CIS_bdpm (orphelins)",
            """
            SELECT COUNT(*) AS nb
            FROM cis_cip_bdpm p
            LEFT JOIN cis_bdpm m ON p.code_cis = m.code_cis
            WHERE m.code_cis IS NULL
            """,
        ),
        (
            "Medicaments SANS composition",
            """
            SELECT COUNT(*) AS nb
            FROM cis_bdpm m
            LEFT JOIN (SELECT DISTINCT code_cis FROM cis_compo_bdpm) c
              ON m.code_cis = c.code_cis
            WHERE c.code_cis IS NULL
            """,
        ),
        (
            "Compositions dont le CIS est absent de CIS_bdpm (orphelins)",
            """
            SELECT COUNT(*) AS nb
            FROM cis_compo_bdpm c
            LEFT JOIN cis_bdpm m ON c.code_cis = m.code_cis
            WHERE m.code_cis IS NULL
            """,
        ),
        (
            "Medicaments SANS groupe generique",
            """
            SELECT COUNT(*) AS nb
            FROM cis_bdpm m
            LEFT JOIN (SELECT DISTINCT code_cis FROM cis_gener_bdpm) g
              ON m.code_cis = g.code_cis
            WHERE g.code_cis IS NULL
            """,
        ),
        (
            "Groupes generiques dont le CIS est absent de CIS_bdpm (orphelins)",
            """
            SELECT COUNT(*) AS nb
            FROM cis_gener_bdpm g
            LEFT JOIN cis_bdpm m ON g.code_cis = m.code_cis
            WHERE m.code_cis IS NULL
            """,
        ),
        (
            "Medicaments avec composition ET presentation",
            """
            SELECT COUNT(*) AS nb
            FROM cis_bdpm m
            INNER JOIN (SELECT DISTINCT code_cis FROM cis_compo_bdpm) c
              ON m.code_cis = c.code_cis
            INNER JOIN (SELECT DISTINCT code_cis FROM cis_cip_bdpm) p
              ON m.code_cis = p.code_cis
            """,
        ),
        (
            "Nombre de CIS distincts par table",
            """
            SELECT 'cis_bdpm' AS table_name, COUNT(DISTINCT code_cis) AS nb_cis FROM cis_bdpm
            UNION ALL
            SELECT 'cis_cip_bdpm', COUNT(DISTINCT code_cis) FROM cis_cip_bdpm
            UNION ALL
            SELECT 'cis_compo_bdpm', COUNT(DISTINCT code_cis) FROM cis_compo_bdpm
            UNION ALL
            SELECT 'cis_gener_bdpm', COUNT(DISTINCT code_cis) FROM cis_gener_bdpm
            """,
        ),
        (
            "Doublons potentiels code_cis dans cis_bdpm",
            """
            SELECT code_cis, COUNT(*) AS nb
            FROM cis_bdpm
            GROUP BY code_cis
            HAVING COUNT(*) > 1
            LIMIT 10
            """,
        ),
        (
            "Doublons potentiels code_cip7 dans cis_cip_bdpm",
            """
            SELECT code_cip7, COUNT(*) AS nb
            FROM cis_cip_bdpm
            GROUP BY code_cip7
            HAVING COUNT(*) > 1
            LIMIT 10
            """,
        ),
        (
            "Patients : effectif + ages invalides",
            """
            SELECT
              (SELECT COUNT(*) FROM healthcare) AS nb_patients,
              (SELECT COUNT(*) FROM healthcare
               WHERE age GLOB '*[^0-9]*'
                  OR CAST(age AS INTEGER) < 0
                  OR CAST(age AS INTEGER) > 120) AS ages_invalides
            """,
        ),
    ]

    for titre, sql in queries:
        print(f"\n> {titre}")
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))


def main() -> None:
    frames = load_sources()
    etudier(frames)
    conn = charger_sqlite(frames)
    coherence_sql(conn)
    conn.close()
    sep("FIN QUESTION 1")
    print("Ouvrir la base avec SQLiteStudio :")
    print(f"  {DB_PATH}")


if __name__ == "__main__":
    main()
