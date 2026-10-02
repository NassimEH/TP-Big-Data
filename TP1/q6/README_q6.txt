TP1 - Question 6
================
Finaliser le schema : cles primaires, etrangeres, contraintes de domaine.

--------------------------------------------------------------------
1) Deja presents depuis le MCD / Q3
--------------------------------------------------------------------
PK :
  Medicaments(idfMedic), Patients(idfPatient), Presentations(idfPresentation),
  Substances(idfSubstance), Groupes(idfGroupe), Laboratoires(idfLabo),
  Prendre(idfPatient, idfMedic, datePrise),
  Composer(idfMedic, idfSubstance, numeroLien),
  Appartenir(idfMedic, idfGroupe), Detenir(idfLabo, idfMedic)

FK :
  Presentations.idfMedic -> Medicaments
  Prendre.idfPatient -> Patients ; Prendre.idfMedic -> Medicaments
  Composer.idfMedic -> Medicaments ; Composer.idfSubstance -> Substances
  Appartenir.idfMedic -> Medicaments ; Appartenir.idfGroupe -> Groupes
  Detenir.idfLabo -> Laboratoires ; Detenir.idfMedic -> Medicaments

--------------------------------------------------------------------
2) Contraintes de domaine ajoutees (Q6)
--------------------------------------------------------------------
Patients.age              : 0..120
Patients.genre            : Male | Female | Other
Presentations.prixMedic   : >= 0 (ou NULL)
Presentations.prixPublic  : >= 0 (ou NULL)
Prendre.posologie         : 1..5
Prendre.duree             : 1..30
Prendre.datePrise         : >= 2025-01-01
Composer.natureComposant  : SA | FT | ST (ou NULL)
Appartenir.typeGenerique  : 0 | 1 | 2 | 4 (ou NULL)
denomination / nom / libelle : non vides

--------------------------------------------------------------------
3) Fichiers
--------------------------------------------------------------------
01_contraintes_integrite.sql   -> DDL final avec PK/FK/CHECK
appliquer_contraintes.py       -> migre q5 -> q6/tp1_cible.db + tests
tp1_cible.db                   -> base finale contrainte
02_preuve_contraintes.txt      -> preuve (inserts refuses)

--------------------------------------------------------------------
4) SQLiteStudio
--------------------------------------------------------------------
Ouvrir TP1/q6/tp1_cible.db
(activer Foreign keys dans les options de connexion si besoin)
