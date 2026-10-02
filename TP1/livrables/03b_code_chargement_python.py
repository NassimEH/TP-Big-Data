# -*- coding: utf-8 -*-
"""
TP1 - Question 5
Charge les donnees dans le schema cible en appliquant les regles de la Q4.
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

Q5_DIR = Path(__file__).resolve().parent
TP1_DIR = Q5_DIR.parent
DATA_DIR = TP1_DIR / "data"
SCHEMA_SQL = TP1_DIR / "q3" / "01_schema_cible.sql"
DB_PATH = Q5_DIR / "tp1_cible.db"
PROOF_PATH = Q5_DIR / "01_preuve_count.txt"

SEED = 42


def parse_price(value: str):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value.replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


def load_sources() -> dict[str, pd.DataFrame]:
    cis = pd.read_csv(
        DATA_DIR / "CIS_bdpm.txt",
        sep="\t",
        header=None,
        names=[
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
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )
    cip = pd.read_csv(
        DATA_DIR / "CIS_CIP_bdpm.txt",
        sep="\t",
        header=None,
        names=[
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
        dtype=str,
        encoding="utf-8",
        keep_default_na=False,
    )
    compo = pd.read_csv(
        DATA_DIR / "CIS_COMPO_bdpm.txt",
        sep="\t",
        header=None,
        names=[
            "code_cis",
            "element_pharmaceutique",
            "code_substance",
            "denomination_substance",
            "dosage",
            "reference_dosage",
            "nature_composant",
            "numero_lien",
        ],
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )
    gener = pd.read_csv(
        DATA_DIR / "CIS_GENER_bdpm.txt",
        sep="\t",
        header=None,
        names=[
            "id_groupe",
            "libelle_groupe",
            "code_cis",
            "type_generique",
            "numero_tri",
        ],
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
    )
    patients = pd.read_csv(
        DATA_DIR / "healthcare_data.csv",
        sep=",",
        dtype=str,
        encoding="utf-8",
        keep_default_na=False,
    )
    return {
        "cis": cis,
        "cip": cip,
        "compo": compo,
        "gener": gener,
        "patients": patients,
    }


def reset_db() -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    return conn


def charger(conn: sqlite3.Connection, src: dict[str, pd.DataFrame]) -> None:
    cis, cip, compo, gener, patients = (
        src["cis"],
        src["cip"],
        src["compo"],
        src["gener"],
        src["patients"],
    )

    # C1 Medicaments
    medicaments = cis[
        ["code_cis", "denomination", "forme", "statut_amm", "date_amm", "numero_autorisation_eu"]
    ].copy()
    medicaments.columns = [
        "idfMedic",
        "denomination",
        "forme",
        "statutAMM",
        "dateAMM",
        "noautorisation",
    ]
    medicaments["idfMedic"] = medicaments["idfMedic"].astype(int)
    medicaments = medicaments.drop_duplicates(subset=["idfMedic"])
    medicaments.to_sql("Medicaments", conn, if_exists="append", index=False)
    medic_ids = set(medicaments["idfMedic"].tolist())
    print(f"Medicaments     : {len(medicaments):,}")

    # C2 Laboratoires + Detenir
    lab_names: list[str] = []
    seen_lab: set[str] = set()
    detenir_rows: list[tuple[int, int]] = []
    for _, row in cis.iterrows():
        mid = int(row["code_cis"])
        raw = (row["titulaires"] or "").strip()
        if not raw:
            continue
        for part in raw.split(";"):
            nom = part.strip()
            if not nom:
                continue
            if nom not in seen_lab:
                seen_lab.add(nom)
                lab_names.append(nom)
            # idfLabo = index+1 after full pass -> resolve later
            detenir_rows.append((nom, mid))

    lab_id = {nom: i + 1 for i, nom in enumerate(lab_names)}
    laboratoires = pd.DataFrame(
        {"idfLabo": [lab_id[n] for n in lab_names], "nom": lab_names}
    )
    laboratoires.to_sql("Laboratoires", conn, if_exists="append", index=False)

    detenir = pd.DataFrame(
        {
            "idfLabo": [lab_id[n] for n, _ in detenir_rows],
            "idfMedic": [m for _, m in detenir_rows],
        }
    ).drop_duplicates()
    detenir = detenir[detenir["idfMedic"].isin(medic_ids)]
    detenir.to_sql("Detenir", conn, if_exists="append", index=False)
    print(f"Laboratoires    : {len(laboratoires):,}")
    print(f"Detenir         : {len(detenir):,}")

    # C4 Substances (avant Composer)
    substances = (
        compo[["code_substance", "denomination_substance"]]
        .rename(
            columns={
                "code_substance": "idfSubstance",
                "denomination_substance": "denomination",
            }
        )
        .drop_duplicates(subset=["idfSubstance"])
    )
    substances = substances[substances["idfSubstance"].str.strip() != ""]
    substances.to_sql("Substances", conn, if_exists="append", index=False)
    print(f"Substances      : {len(substances):,}")

    # C6 Groupes
    groupes = (
        gener[["id_groupe", "libelle_groupe"]]
        .rename(columns={"id_groupe": "idfGroupe", "libelle_groupe": "libelle"})
        .drop_duplicates(subset=["idfGroupe"])
    )
    groupes["idfGroupe"] = groupes["idfGroupe"].astype(int)
    groupes.to_sql("Groupes", conn, if_exists="append", index=False)
    print(f"Groupes         : {len(groupes):,}")

    # C8 Patients
    pat = patients[
        ["patient_id", "first_name", "last_name", "age", "gender", "email"]
    ].copy()
    pat.columns = ["idfPatient", "prenom", "nom", "age", "genre", "mail"]
    pat["age"] = pd.to_numeric(pat["age"], errors="coerce").astype("Int64")
    pat = pat.drop_duplicates(subset=["idfPatient"])
    # SQLite via to_sql: convert NA age
    pat["age"] = pat["age"].astype(object).where(pat["age"].notna(), None)
    pat.to_sql("Patients", conn, if_exists="append", index=False)
    print(f"Patients        : {len(pat):,}")

    # C3 Presentations (FK medicaments)
    pres = cip.copy()
    pres = pres[pres["code_cis"].map(lambda x: int(x) if x.isdigit() else None).isin(medic_ids)]
    presentations = pd.DataFrame(
        {
            "idfPresentation": pres["code_cip7"],
            "libelle": pres["libelle"],
            "statutADM": pres["statut_admin"],
            "dateCom": pres["date_declaration_com"],
            "tauxRembt": pres["taux_remboursement"],
            "prixMedic": pres["prix_medicament"].map(parse_price),
            "prixPublic": pres["prix_public"].map(parse_price),
            "idfMedic": pres["code_cis"].astype(int),
        }
    ).drop_duplicates(subset=["idfPresentation"])
    presentations.to_sql("Presentations", conn, if_exists="append", index=False)
    print(f"Presentations   : {len(presentations):,}")

    # C5 Composer
    comp = compo.copy()
    comp["idfMedic"] = pd.to_numeric(comp["code_cis"], errors="coerce")
    comp = comp[comp["idfMedic"].isin(medic_ids)]
    subst_ids = set(substances["idfSubstance"])
    comp = comp[comp["code_substance"].isin(subst_ids)]
    comp["numero_lien"] = comp["numero_lien"].replace("", "1")
    composer = pd.DataFrame(
        {
            "idfMedic": comp["idfMedic"].astype(int),
            "idfSubstance": comp["code_substance"],
            "dosage": comp["dosage"],
            "refDosage": comp["reference_dosage"],
            "natureComposant": comp["nature_composant"],
            "elementPharma": comp["element_pharmaceutique"],
            "numeroLien": comp["numero_lien"],
        }
    ).drop_duplicates(subset=["idfMedic", "idfSubstance", "numeroLien"])
    composer.to_sql("Composer", conn, if_exists="append", index=False)
    print(f"Composer        : {len(composer):,}")

    # C7 Appartenir
    app = gener.copy()
    app["idfMedic"] = pd.to_numeric(app["code_cis"], errors="coerce")
    app = app[app["idfMedic"].isin(medic_ids)]
    appartenir = pd.DataFrame(
        {
            "idfMedic": app["idfMedic"].astype(int),
            "idfGroupe": app["id_groupe"].astype(int),
            "typeGenerique": pd.to_numeric(app["type_generique"], errors="coerce"),
            "numeroTri": pd.to_numeric(app["numero_tri"], errors="coerce"),
        }
    ).drop_duplicates(subset=["idfMedic", "idfGroupe"])
    appartenir.to_sql("Appartenir", conn, if_exists="append", index=False)
    print(f"Appartenir      : {len(appartenir):,}")

    # C9 Generer Prendre
    rng = random.Random(SEED)
    start = date(2025, 1, 1)
    end = date.today()
    span = (end - start).days
    if span < 0:
        span = 0

    medic_list = list(medic_ids)
    prendre_rows: list[tuple] = []
    for pid in pat["idfPatient"].tolist():
        k = rng.randint(1, 10)
        chosen = rng.sample(medic_list, k=min(k, len(medic_list)))
        for mid in chosen:
            d = start + timedelta(days=rng.randint(0, span))
            posologie = rng.randint(1, 5)
            duree = rng.randint(1, 30)
            prendre_rows.append((pid, mid, d.isoformat(), posologie, duree))

    prendre = pd.DataFrame(
        prendre_rows,
        columns=["idfPatient", "idfMedic", "datePrise", "posologie", "duree"],
    ).drop_duplicates(subset=["idfPatient", "idfMedic", "datePrise"])
    prendre.to_sql("Prendre", conn, if_exists="append", index=False)
    print(f"Prendre         : {len(prendre):,}  (seed={SEED})")

    conn.commit()


def preuve(conn: sqlite3.Connection) -> None:
    tables = [
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
    lines = [
        "TP1 - Question 5 - Preuve de chargement (COUNT(*))",
        "=" * 55,
        f"Base : {DB_PATH.resolve()}",
        f"Seed Prendre : {SEED}",
        "",
    ]
    print("\n--- COUNT(*) ---")
    for t in tables:
        n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        lines.append(f"SELECT COUNT(*) FROM {t};  -->  {n}")
        print(f"{t:<16} {n:,}")

    # controles FK rapides
    checks = [
        (
            "Presentations orphelines",
            """
            SELECT COUNT(*) FROM Presentations p
            LEFT JOIN Medicaments m ON p.idfMedic = m.idfMedic
            WHERE m.idfMedic IS NULL
            """,
        ),
        (
            "Prendre orphelins patient",
            """
            SELECT COUNT(*) FROM Prendre x
            LEFT JOIN Patients p ON x.idfPatient = p.idfPatient
            WHERE p.idfPatient IS NULL
            """,
        ),
        (
            "Prendre orphelins medic",
            """
            SELECT COUNT(*) FROM Prendre x
            LEFT JOIN Medicaments m ON x.idfMedic = m.idfMedic
            WHERE m.idfMedic IS NULL
            """,
        ),
        (
            "Patients sans medicament (doit etre 0)",
            """
            SELECT COUNT(*) FROM Patients p
            LEFT JOIN Prendre x ON p.idfPatient = x.idfPatient
            WHERE x.idfPatient IS NULL
            """,
        ),
    ]
    lines.append("")
    lines.append("Controles de coherence :")
    print("\n--- Controles ---")
    for titre, sql in checks:
        n = conn.execute(sql).fetchone()[0]
        lines.append(f"- {titre} : {n}")
        print(f"{titre}: {n}")

    PROOF_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nPreuve ecrite : {PROOF_PATH}")


def main() -> None:
    print("Chargement Q5 ...")
    src = load_sources()
    conn = reset_db()
    try:
        charger(conn, src)
        preuve(conn)
    finally:
        conn.close()
    print("\nOK - ouvrir dans SQLiteStudio :")
    print(f"  {DB_PATH}")


if __name__ == "__main__":
    main()
