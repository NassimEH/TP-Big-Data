-- =============================================================================
-- TP1 - Question 6
-- Finalisation du schema : cles primaires, etrangeres, contraintes de domaine
-- SGBD : SQLite (PRAGMA foreign_keys = ON)
--
-- Note SQLite : les CHECK se definissent a la creation de table.
-- Ce script recree le schema enrichi (a utiliser avec appliquer_contraintes.py
-- qui migre les donnees depuis q5/tp1_cible.db).
-- =============================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Detenir;
DROP TABLE IF EXISTS Appartenir;
DROP TABLE IF EXISTS Composer;
DROP TABLE IF EXISTS Prendre;
DROP TABLE IF EXISTS Presentations;
DROP TABLE IF EXISTS Substances;
DROP TABLE IF EXISTS Groupes;
DROP TABLE IF EXISTS Laboratoires;
DROP TABLE IF EXISTS Patients;
DROP TABLE IF EXISTS Medicaments;

-- ---------------------------------------------------------------------------
-- Entites (+ contraintes de domaine)
-- ---------------------------------------------------------------------------

CREATE TABLE Medicaments (
  idfMedic         INTEGER      PRIMARY KEY,
  denomination     TEXT         NOT NULL,
  forme            TEXT,
  statutAMM        TEXT,
  dateAMM          TEXT,
  noautorisation   TEXT,
  CHECK (length(trim(denomination)) > 0)
);

CREATE TABLE Patients (
  idfPatient       TEXT         PRIMARY KEY,
  prenom           TEXT,
  nom              TEXT,
  age              INTEGER,
  genre            TEXT,
  mail             TEXT,
  CHECK (age IS NULL OR (age >= 0 AND age <= 120)),
  CHECK (genre IS NULL OR genre IN ('Male', 'Female', 'Other'))
);

CREATE TABLE Presentations (
  idfPresentation  TEXT         PRIMARY KEY,
  libelle          TEXT,
  statutADM        TEXT,
  dateCom          TEXT,
  tauxRembt        TEXT,
  prixMedic        REAL,
  prixPublic       REAL,
  idfMedic         INTEGER      NOT NULL,
  CHECK (prixMedic IS NULL OR prixMedic >= 0),
  CHECK (prixPublic IS NULL OR prixPublic >= 0),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Substances (
  idfSubstance     TEXT         PRIMARY KEY,
  denomination     TEXT         NOT NULL,
  CHECK (length(trim(denomination)) > 0)
);

CREATE TABLE Groupes (
  idfGroupe        INTEGER      PRIMARY KEY,
  libelle          TEXT         NOT NULL,
  CHECK (length(trim(libelle)) > 0)
);

CREATE TABLE Laboratoires (
  idfLabo          INTEGER      PRIMARY KEY,
  nom              TEXT         NOT NULL,
  CHECK (length(trim(nom)) > 0)
);

-- ---------------------------------------------------------------------------
-- Associations (+ domaines issus du sujet Q4)
-- ---------------------------------------------------------------------------

CREATE TABLE Prendre (
  idfPatient       TEXT         NOT NULL,
  idfMedic         INTEGER      NOT NULL,
  datePrise        TEXT         NOT NULL,
  posologie        INTEGER      NOT NULL,
  duree            INTEGER      NOT NULL,
  PRIMARY KEY (idfPatient, idfMedic, datePrise),
  CHECK (posologie BETWEEN 1 AND 5),
  CHECK (duree BETWEEN 1 AND 30),
  CHECK (datePrise >= '2025-01-01'),
  FOREIGN KEY (idfPatient) REFERENCES Patients(idfPatient),
  FOREIGN KEY (idfMedic)   REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Composer (
  idfMedic         INTEGER      NOT NULL,
  idfSubstance     TEXT         NOT NULL,
  dosage           TEXT,
  refDosage        TEXT,
  natureComposant  TEXT,
  elementPharma    TEXT,
  numeroLien       TEXT         NOT NULL DEFAULT '1',
  PRIMARY KEY (idfMedic, idfSubstance, numeroLien),
  CHECK (natureComposant IS NULL OR natureComposant IN ('SA', 'FT', 'ST')),
  FOREIGN KEY (idfMedic)     REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfSubstance) REFERENCES Substances(idfSubstance)
);

CREATE TABLE Appartenir (
  idfMedic         INTEGER      NOT NULL,
  idfGroupe        INTEGER      NOT NULL,
  typeGenerique    INTEGER,
  numeroTri        INTEGER,
  PRIMARY KEY (idfMedic, idfGroupe),
  CHECK (typeGenerique IS NULL OR typeGenerique IN (0, 1, 2, 4)),
  FOREIGN KEY (idfMedic)  REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfGroupe) REFERENCES Groupes(idfGroupe)
);

CREATE TABLE Detenir (
  idfLabo          INTEGER      NOT NULL,
  idfMedic         INTEGER      NOT NULL,
  PRIMARY KEY (idfLabo, idfMedic),
  FOREIGN KEY (idfLabo)  REFERENCES Laboratoires(idfLabo),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE INDEX idx_presentations_medic ON Presentations(idfMedic);
CREATE INDEX idx_prendre_medic       ON Prendre(idfMedic);
CREATE INDEX idx_composer_substance  ON Composer(idfSubstance);
CREATE INDEX idx_appartenir_groupe   ON Appartenir(idfGroupe);
CREATE INDEX idx_detenir_medic       ON Detenir(idfMedic);
