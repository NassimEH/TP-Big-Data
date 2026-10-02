# -*- coding: utf-8 -*-
"""
TP1 - Etape 2 / Question 2
Analyse des donnees integrees avec ydata_profiling.
Produit un rapport HTML + synthese texte pour le livrable.
"""

from __future__ import annotations

import sqlite3
import warnings
from pathlib import Path

import pandas as pd

ETAPE2 = Path(__file__).resolve().parent
DB = ETAPE2.parent / "q6" / "tp1_cible.db"
HTML_OUT = ETAPE2 / "03_profil_ydata.html"
TXT_OUT = ETAPE2 / "04_analyse_integration.txt"


def load_frames(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    # Tables principales ; Prendre echantillonne pour rester raisonnable
    frames = {
        "Patients": pd.read_sql_query("SELECT * FROM Patients", conn),
        "Medicaments": pd.read_sql_query("SELECT * FROM Medicaments", conn),
        "Presentations": pd.read_sql_query(
            """
            SELECT idfPresentation, libelle, statutADM, dateCom, tauxRembt,
                   prixMedic, prixPublic, idfMedic
            FROM Presentations
            """,
            conn,
        ),
        "Prendre": pd.read_sql_query(
            """
            SELECT idfPatient, idfMedic, datePrise, posologie, duree
            FROM Prendre
            ORDER BY RANDOM()
            LIMIT 20000
            """,
            conn,
        ),
        "Composer": pd.read_sql_query(
            """
            SELECT idfMedic, idfSubstance, dosage, refDosage, natureComposant
            FROM Composer
            ORDER BY RANDOM()
            LIMIT 15000
            """,
            conn,
        ),
        "Appartenir": pd.read_sql_query("SELECT * FROM Appartenir", conn),
    }
    return frames


def profile_all(frames: dict[str, pd.DataFrame]) -> None:
    from ydata_profiling import ProfileReport

    # Un rapport multi-tables via concatenation taggede
    # (ProfileReport accepte un seul DF : on fait un rapport par table
    #  puis on synthese, et un HTML principal sur Patients+Prendre joint)
    warnings.filterwarnings("ignore")

    patients = frames["Patients"].copy()
    prendre = frames["Prendre"].copy()
    merged = prendre.merge(patients, on="idfPatient", how="left")
    merged = merged.merge(
        frames["Medicaments"][["idfMedic", "denomination", "forme", "statutAMM"]],
        on="idfMedic",
        how="left",
    )

    report = ProfileReport(
        merged,
        title="TP1 Big Data - Analyse post-integration (Patients x Prendre x Medicaments)",
        explorative=True,
        minimal=False,
        correlations={"auto": {"calculate": True}},
        interactions={"continuous": False},
    )
    report.to_file(HTML_OUT)
    print("HTML:", HTML_OUT)

    # Rapports legers par table (optionnels, pour stats texte)
    summaries = []
    for name, df in frames.items():
        summaries.append(summarize_df(name, df))
    summaries.append(summarize_df("Vue_Prendre_Patients_Medicaments", merged))
    return summaries


def summarize_df(name: str, df: pd.DataFrame) -> str:
    lines = [f"### Table / vue : {name}", f"- Lignes : {len(df):,}", f"- Colonnes : {len(df.columns)}"]
    nulls = df.isna().sum()
    nulls = nulls[nulls > 0]
    if len(nulls):
        lines.append("- Valeurs manquantes :")
        for col, n in nulls.sort_values(ascending=False).head(8).items():
            pct = 100.0 * n / len(df)
            lines.append(f"    - {col}: {n:,} ({pct:.1f}%)")
    else:
        lines.append("- Valeurs manquantes : aucune")

    # numeriques
    num = df.select_dtypes(include="number")
    if not num.empty:
        lines.append("- Stats numeriques :")
        desc = num.describe().T[["mean", "std", "min", "max"]]
        for col, row in desc.iterrows():
            lines.append(
                f"    - {col}: mean={row['mean']:.2f}, std={row['std']:.2f}, "
                f"min={row['min']:.2f}, max={row['max']:.2f}"
            )

    # categoriques courtes
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype) == "string":
            nunq = df[col].nunique(dropna=True)
            if 1 < nunq <= 12:
                vc = df[col].value_counts(dropna=False).head(8)
                lines.append(f"- Distribution {col} ({nunq} modalites) :")
                for k, v in vc.items():
                    lines.append(f"    - {k}: {v:,}")
    lines.append("")
    return "\n".join(lines)


def extra_sql_insights(conn: sqlite3.Connection) -> str:
    q = """
    SELECT
      (SELECT COUNT(*) FROM Medicaments) AS medicaments,
      (SELECT COUNT(*) FROM Presentations) AS presentations,
      (SELECT ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Medicaments), 1)
         FROM Medicaments m
         WHERE EXISTS (SELECT 1 FROM Presentations p WHERE p.idfMedic = m.idfMedic)
      ) AS pct_medic_avec_presentation,
      (SELECT ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Medicaments), 1)
         FROM Medicaments m
         WHERE EXISTS (SELECT 1 FROM Composer c WHERE c.idfMedic = m.idfMedic)
      ) AS pct_medic_avec_compo,
      (SELECT ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Medicaments), 1)
         FROM Medicaments m
         WHERE EXISTS (SELECT 1 FROM Appartenir a WHERE a.idfMedic = m.idfMedic)
      ) AS pct_medic_avec_groupe,
      (SELECT ROUND(AVG(prixMedic), 2) FROM Presentations WHERE prixMedic IS NOT NULL) AS prix_medic_moyen,
      (SELECT ROUND(AVG(age), 1) FROM Patients) AS age_moyen_patients,
      (SELECT COUNT(*) FROM Prendre) AS nb_prises
    """
    row = pd.read_sql_query(q, conn).iloc[0]
    return "\n".join(
        [
            "### Indicateurs SQL post-integration",
            f"- Medicaments : {int(row.medicaments):,}",
            f"- Presentations : {int(row.presentations):,}",
            f"- % medicaments avec presentation : {row.pct_medic_avec_presentation}%",
            f"- % medicaments avec composition : {row.pct_medic_avec_compo}%",
            f"- % medicaments dans un groupe generique : {row.pct_medic_avec_groupe}%",
            f"- Prix medicament moyen (presentations) : {row.prix_medic_moyen} EUR",
            f"- Age moyen patients : {row.age_moyen_patients}",
            f"- Nombre de prises generees : {int(row.nb_prises):,}",
            "",
        ]
    )


def write_analysis(summaries: list[str], sql_block: str) -> None:
    text = [
        "TP1 - Etape 2 - Analyse des donnees apres integration",
        "=" * 70,
        "",
        "Outil : ydata_profiling (ProfileReport)",
        f"Rapport HTML detaille : {HTML_OUT.name}",
        "Perimetre : jointure Patients x Prendre (echantillon) x Medicaments,",
        "plus profils descriptifs des tables sources integrees.",
        "",
        "Synthese",
        "-" * 70,
        "Les donnees BDPM et healthcare ont ete integrees dans le schema cible",
        "(q6/tp1_cible.db) avec contraintes d'integrite. L'association Prendre",
        "a ete generee aleatoirement (1 a 10 medicaments par patient).",
        "",
        "Constats principaux :",
        "- Patients : ages entre 1 et 90, genres Male/Female/Other equilibres.",
        "- Presentations : nombreux prix manquants (non rembourses / non renseignes).",
        "- Composer : natureComposant principalement SA (substance active) et FT.",
        "- Appartenir : types generiques 0/1/2/4 conformes au referentiel BDPM.",
        "- Couverture incomplete : une partie des medicaments n'a pas de presentation",
        "  ou de groupe generique (coherent avec l'etude de coherence Q1).",
        "- Prendre : posologies 1-5 et durees 1-30 respectent les contraintes Q6.",
        "",
        sql_block,
        "Details par table",
        "-" * 70,
        "",
    ]
    text.extend(summaries)
    text.append(
        "Conclusion : le jeu de donnees integre est exploitable pour des statistiques\n"
        "SQL (etape 2.1) et pour un profiling exploratoire. Les valeurs manquantes\n"
        "sur les prix et l'absence de certains liens CIS restent les principaux\n"
        "points de qualite a surveiller.\n"
    )
    TXT_OUT.write_text("\n".join(text), encoding="utf-8")
    print("TXT:", TXT_OUT)


def main() -> None:
    conn = sqlite3.connect(DB)
    try:
        frames = load_frames(conn)
        sql_block = extra_sql_insights(conn)
        for k, df in frames.items():
            print(f"charge {k}: {len(df):,} x {len(df.columns)}")
        summaries = profile_all(frames)
        write_analysis(summaries, sql_block)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
