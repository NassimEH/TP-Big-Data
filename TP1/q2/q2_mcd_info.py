# -*- coding: utf-8 -*-
"""
TP1 - Question 2
Retroconception du schema relationnel cible et modele conceptuel de donnees (MCD).

Outil recommande par le sujet : Looping-MCD
  https://www.looping-mcd.fr/
  (logiciel desktop libre - Universite de Toulouse)

Livrables dans ce dossier :
  - 01_retroconception.txt : analyse du schema cible du sujet
  - 02_mcd.txt             : MCD complet (entites, associations, cardinalites)
  - mcd.mmd                : diagramme Mermaid (apercu / rendu)
  - guide_looping.txt      : etapes pour reproduire le MCD dans Looping
"""

from pathlib import Path

Q2_DIR = Path(__file__).resolve().parent
TP1_DIR = Q2_DIR.parent


def main() -> None:
    print("Question 2 = modelisation (pas d'execution de code metier).")
    print(f"Dossier Q2 : {Q2_DIR}")
    print(f"Donnees TP1 : {TP1_DIR / 'data'}")
    print("Ouvrir 02_mcd.txt et mcd.mmd, puis recreer le schema dans Looping-MCD.")


if __name__ == "__main__":
    main()
