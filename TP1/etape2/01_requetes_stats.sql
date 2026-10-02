-- =============================================================================
-- TP1 - Etape 2 / Question 1
-- 10 requetes SQL statistiques (dont >= 6 avec GROUP BY)
-- Base : TP1/q6/tp1_cible.db
-- =============================================================================

-- Q01 [GROUP BY] Nombre de presentations par medicament (top 15)
SELECT m.idfMedic,
       m.denomination,
       COUNT(p.idfPresentation) AS nb_presentations
FROM Medicaments m
LEFT JOIN Presentations p ON p.idfMedic = m.idfMedic
GROUP BY m.idfMedic, m.denomination
ORDER BY nb_presentations DESC
LIMIT 15;

-- Q02 [GROUP BY] Nombre de medicaments par laboratoire (top 15)
SELECT l.nom AS laboratoire,
       COUNT(d.idfMedic) AS nb_medicaments
FROM Laboratoires l
JOIN Detenir d ON d.idfLabo = l.idfLabo
GROUP BY l.idfLabo, l.nom
ORDER BY nb_medicaments DESC
LIMIT 15;

-- Q03 [GROUP BY] Effectif patients par genre
SELECT genre,
       COUNT(*) AS nb_patients,
       ROUND(AVG(age), 1) AS age_moyen,
       MIN(age) AS age_min,
       MAX(age) AS age_max
FROM Patients
GROUP BY genre
ORDER BY nb_patients DESC;

-- Q04 [GROUP BY] Nombre de prises par patient (distribution)
SELECT nb_prises, COUNT(*) AS nb_patients
FROM (
  SELECT idfPatient, COUNT(*) AS nb_prises
  FROM Prendre
  GROUP BY idfPatient
)
GROUP BY nb_prises
ORDER BY nb_prises;

-- Q05 [GROUP BY] Top 15 substances les plus utilisees (nb medicaments)
SELECT s.denomination AS substance,
       COUNT(DISTINCT c.idfMedic) AS nb_medicaments,
       COUNT(*) AS nb_lignes_compo
FROM Substances s
JOIN Composer c ON c.idfSubstance = s.idfSubstance
GROUP BY s.idfSubstance, s.denomination
ORDER BY nb_medicaments DESC
LIMIT 15;

-- Q06 [GROUP BY] Medicaments par type generique
SELECT CASE typeGenerique
         WHEN 0 THEN '0 - princeps'
         WHEN 1 THEN '1 - generique'
         WHEN 2 THEN '2 - complementarite posologique'
         WHEN 4 THEN '4 - generique substituable'
         ELSE 'autre/NULL'
       END AS type_generique,
       COUNT(*) AS nb_appartenances,
       COUNT(DISTINCT idfMedic) AS nb_medicaments,
       COUNT(DISTINCT idfGroupe) AS nb_groupes
FROM Appartenir
GROUP BY typeGenerique
ORDER BY typeGenerique;

-- Q07 [GROUP BY] Prix moyen des presentations par taux de remboursement (top)
SELECT COALESCE(NULLIF(tauxRembt, ''), '(vide)') AS taux_remboursement,
       COUNT(*) AS nb_presentations,
       ROUND(AVG(prixMedic), 2) AS prix_medic_moyen,
       ROUND(AVG(prixPublic), 2) AS prix_public_moyen
FROM Presentations
GROUP BY tauxRembt
ORDER BY nb_presentations DESC
LIMIT 15;

-- Q08 Statistique globale : volumes et couverture
SELECT
  (SELECT COUNT(*) FROM Medicaments) AS nb_medicaments,
  (SELECT COUNT(*) FROM Presentations) AS nb_presentations,
  (SELECT COUNT(*) FROM Patients) AS nb_patients,
  (SELECT COUNT(*) FROM Prendre) AS nb_prises,
  (SELECT COUNT(*) FROM Substances) AS nb_substances,
  (SELECT COUNT(*) FROM Groupes) AS nb_groupes,
  (SELECT COUNT(*) FROM Laboratoires) AS nb_laboratoires,
  (SELECT ROUND(AVG(nb), 2) FROM (
      SELECT COUNT(*) AS nb FROM Prendre GROUP BY idfPatient
  )) AS nb_moyen_prises_par_patient;

-- Q09 Top 15 medicaments les plus prescrits (via Prendre)
SELECT m.idfMedic,
       m.denomination,
       m.forme,
       COUNT(*) AS nb_prises,
       COUNT(DISTINCT pr.idfPatient) AS nb_patients_distincts,
       ROUND(AVG(pr.posologie), 2) AS posologie_moyenne,
       ROUND(AVG(pr.duree), 1) AS duree_moyenne
FROM Prendre pr
JOIN Medicaments m ON m.idfMedic = pr.idfMedic
GROUP BY m.idfMedic, m.denomination, m.forme
ORDER BY nb_prises DESC
LIMIT 15;

-- Q10 Statistiques d'age des patients ayant au moins une prise
--     + correlation simple : nb prises moyen par tranche d'age
SELECT
  CASE
    WHEN age < 18 THEN '0-17'
    WHEN age BETWEEN 18 AND 39 THEN '18-39'
    WHEN age BETWEEN 40 AND 64 THEN '40-64'
    ELSE '65+'
  END AS tranche_age,
  COUNT(DISTINCT p.idfPatient) AS nb_patients,
  COUNT(pr.idfMedic) AS nb_prises,
  ROUND(1.0 * COUNT(pr.idfMedic) / COUNT(DISTINCT p.idfPatient), 2) AS prises_par_patient,
  ROUND(AVG(pr.posologie), 2) AS posologie_moyenne
FROM Patients p
JOIN Prendre pr ON pr.idfPatient = p.idfPatient
GROUP BY
  CASE
    WHEN age < 18 THEN '0-17'
    WHEN age BETWEEN 18 AND 39 THEN '18-39'
    WHEN age BETWEEN 40 AND 64 THEN '40-64'
    ELSE '65+'
  END
ORDER BY tranche_age;
