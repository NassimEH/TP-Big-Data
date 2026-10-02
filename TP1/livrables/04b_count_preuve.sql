-- TP1 Q5 - Preuves COUNT(*) a rejouer dans SQLiteStudio
-- Base : TP1/q5/tp1_cible.db

SELECT 'Medicaments' AS table_name, COUNT(*) AS nb FROM Medicaments
UNION ALL SELECT 'Patients', COUNT(*) FROM Patients
UNION ALL SELECT 'Presentations', COUNT(*) FROM Presentations
UNION ALL SELECT 'Substances', COUNT(*) FROM Substances
UNION ALL SELECT 'Groupes', COUNT(*) FROM Groupes
UNION ALL SELECT 'Laboratoires', COUNT(*) FROM Laboratoires
UNION ALL SELECT 'Prendre', COUNT(*) FROM Prendre
UNION ALL SELECT 'Composer', COUNT(*) FROM Composer
UNION ALL SELECT 'Appartenir', COUNT(*) FROM Appartenir
UNION ALL SELECT 'Detenir', COUNT(*) FROM Detenir;
