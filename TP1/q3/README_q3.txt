TP1 - Question 3
================
Generer le schema relationnel SQL a partir du MCD et l'executer.

--------------------------------------------------------------------
1) Principe (MCD -> relationnel)
--------------------------------------------------------------------
- Chaque ENTITE        -> une TABLE (+ cle primaire)
- Association 1,n      -> cle etrangere cote cardinalite (1,1)
    ex: Presentations.idfMedic -> Medicaments
- Association n,n      -> TABLE d'association
    (+ attributs portes : datePrise, dosage, typeGenerique, ...)

--------------------------------------------------------------------
2) Fichiers de ce dossier
--------------------------------------------------------------------
01_schema_cible.sql   -> script SQL a executer (SQLiteStudio ou Python)
executer_schema.py    -> cree automatiquement tp1_cible.db
tp1_cible.db          -> base SQLite du schema CIBLE (vide, prete au chargement Q4/Q5)
02_preuve_execution.txt -> liste des tables apres execution

--------------------------------------------------------------------
3) Execution manuelle dans SQLiteStudio
--------------------------------------------------------------------
1. Database > Add a database > creer/ouvrir TP1/q3/tp1_cible.db
2. Tools > Open SQL editor
3. Ouvrir 01_schema_cible.sql
4. Executer tout le script (Execute all / F9)
5. Verifier les 10 tables dans l'explorateur

--------------------------------------------------------------------
4) Ou en une commande
--------------------------------------------------------------------
  python TP1/q3/executer_schema.py
