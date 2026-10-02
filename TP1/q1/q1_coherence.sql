-- =============================================================================
-- TP1 - Question 1 : verification de coherence (SQLiteStudio)
-- Base : TP1/q1/tp1_initial.db
-- Usage : Database > Add a database > ouvrir TP1/q1/tp1_initial.db
--         Tools > Open SQL editor > ouvrir ce fichier
--         Executer bloc par bloc (selectionner une requete puis Ctrl+Enter)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0) Effectifs (preuve de chargement)
-- Attendus : 15883 / 20925 / 32439 / 10737 / 17498
-- -----------------------------------------------------------------------------
SELECT 'cis_bdpm' AS table_name, COUNT(*) AS nb FROM cis_bdpm
UNION ALL
SELECT 'cis_cip_bdpm', COUNT(*) FROM cis_cip_bdpm
UNION ALL
SELECT 'cis_compo_bdpm', COUNT(*) FROM cis_compo_bdpm
UNION ALL
SELECT 'cis_gener_bdpm', COUNT(*) FROM cis_gener_bdpm
UNION ALL
SELECT 'healthcare', COUNT(*) FROM healthcare;


-- -----------------------------------------------------------------------------
-- 1) Medicaments SANS aucune presentation (CIP)
-- Attendu : 1249
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_medicaments_sans_presentation
FROM cis_bdpm m
LEFT JOIN (SELECT DISTINCT code_cis FROM cis_cip_bdpm) p
  ON m.code_cis = p.code_cis
WHERE p.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 2) Presentations dont le CIS est absent de cis_bdpm (orphelins)
-- Attendu : 4
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_cip_orphelins
FROM cis_cip_bdpm p
LEFT JOIN cis_bdpm m ON p.code_cis = m.code_cis
WHERE m.code_cis IS NULL;


-- Detail des CIP orphelins (optionnel)
SELECT p.code_cis, p.code_cip7, p.libelle
FROM cis_cip_bdpm p
LEFT JOIN cis_bdpm m ON p.code_cis = m.code_cis
WHERE m.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 3) Medicaments SANS composition
-- Attendu : 2
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_medicaments_sans_composition
FROM cis_bdpm m
LEFT JOIN (SELECT DISTINCT code_cis FROM cis_compo_bdpm) c
  ON m.code_cis = c.code_cis
WHERE c.code_cis IS NULL;


-- Detail (optionnel)
SELECT m.code_cis, m.denomination
FROM cis_bdpm m
LEFT JOIN (SELECT DISTINCT code_cis FROM cis_compo_bdpm) c
  ON m.code_cis = c.code_cis
WHERE c.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 4) Compositions dont le CIS est absent de cis_bdpm (orphelins)
-- Attendu : 0
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_compo_orphelins
FROM cis_compo_bdpm c
LEFT JOIN cis_bdpm m ON c.code_cis = m.code_cis
WHERE m.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 5) Medicaments SANS groupe generique
-- Attendu : 7692
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_medicaments_sans_groupe
FROM cis_bdpm m
LEFT JOIN (SELECT DISTINCT code_cis FROM cis_gener_bdpm) g
  ON m.code_cis = g.code_cis
WHERE g.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 6) Groupes generiques dont le CIS est absent de cis_bdpm (orphelins)
-- Attendu : 2483
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_gener_orphelins
FROM cis_gener_bdpm g
LEFT JOIN cis_bdpm m ON g.code_cis = m.code_cis
WHERE m.code_cis IS NULL;


-- -----------------------------------------------------------------------------
-- 7) Medicaments avec composition ET presentation
-- Attendu : 14632
-- -----------------------------------------------------------------------------
SELECT COUNT(*) AS nb_medicaments_complets
FROM cis_bdpm m
INNER JOIN (SELECT DISTINCT code_cis FROM cis_compo_bdpm) c
  ON m.code_cis = c.code_cis
INNER JOIN (SELECT DISTINCT code_cis FROM cis_cip_bdpm) p
  ON m.code_cis = p.code_cis;


-- -----------------------------------------------------------------------------
-- 8) Nombre de CIS distincts par table
-- Attendus : 15883 / 14638 / 15881 / 10661
-- -----------------------------------------------------------------------------
SELECT 'cis_bdpm' AS table_name, COUNT(DISTINCT code_cis) AS nb_cis FROM cis_bdpm
UNION ALL
SELECT 'cis_cip_bdpm', COUNT(DISTINCT code_cis) FROM cis_cip_bdpm
UNION ALL
SELECT 'cis_compo_bdpm', COUNT(DISTINCT code_cis) FROM cis_compo_bdpm
UNION ALL
SELECT 'cis_gener_bdpm', COUNT(DISTINCT code_cis) FROM cis_gener_bdpm;


-- -----------------------------------------------------------------------------
-- 9) Doublons code_cis dans cis_bdpm
-- Attendu : aucune ligne
-- -----------------------------------------------------------------------------
SELECT code_cis, COUNT(*) AS nb
FROM cis_bdpm
GROUP BY code_cis
HAVING COUNT(*) > 1
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 10) Doublons code_cip7 dans cis_cip_bdpm
-- Attendu : aucune ligne
-- -----------------------------------------------------------------------------
SELECT code_cip7, COUNT(*) AS nb
FROM cis_cip_bdpm
GROUP BY code_cip7
HAVING COUNT(*) > 1
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 11) Patients : effectif + ages invalides
-- Attendu : 17498 patients, 0 ages invalides
-- -----------------------------------------------------------------------------
SELECT
  (SELECT COUNT(*) FROM healthcare) AS nb_patients,
  (SELECT COUNT(*) FROM healthcare
   WHERE age GLOB '*[^0-9]*'
      OR CAST(age AS INTEGER) < 0
      OR CAST(age AS INTEGER) > 120) AS ages_invalides;
