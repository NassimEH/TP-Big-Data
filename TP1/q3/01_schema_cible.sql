-- =============================================================================
-- TP1 - Question 3
-- Schema relationnel SQL genere a partir du MCD (Looping / q2)
-- SGBD : SQLite (SQLiteStudio)
-- Base cible : TP1/q3/tp1_cible.db
--
-- Correspondance MCD -> relations :
--   Entite            -> table
--   Association 1,n   -> FK cote (1,1)  ex: Presentations.idfMedic
--   Association n,n   -> table association (Prendre, Composer, Appartenir, Detenir)
-- =============================================================================

PRAGMA foreign_keys = ON;

-- Nettoyage (rejouable)
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
-- Entites
-- ---------------------------------------------------------------------------

CREATE TABLE Medicaments (
  idfMedic         INTEGER      PRIMARY KEY,
  denomination     TEXT         NOT NULL,
  forme            TEXT,
  statutAMM        TEXT,
  dateAMM          TEXT,          -- JJ/MM/AAAA ou ISO
  noautorisation   TEXT
);

CREATE TABLE Patients (
  idfPatient       TEXT         PRIMARY KEY,
  prenom           TEXT,
  nom              TEXT,
  age              INTEGER,
  genre            TEXT,
  mail             TEXT
);

CREATE TABLE Presentations (
  idfPresentation  TEXT         PRIMARY KEY,   -- code CIP7
  libelle          TEXT,
  statutADM        TEXT,
  dateCom          TEXT,
  tauxRembt        TEXT,
  prixMedic        REAL,
  prixPublic       REAL,
  idfMedic         INTEGER      NOT NULL,
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Substances (
  idfSubstance     TEXT         PRIMARY KEY,
  denomination     TEXT         NOT NULL
);

CREATE TABLE Groupes (
  idfGroupe        INTEGER      PRIMARY KEY,
  libelle          TEXT         NOT NULL
);

CREATE TABLE Laboratoires (
  idfLabo          INTEGER      PRIMARY KEY,
  nom              TEXT         NOT NULL
);

-- ---------------------------------------------------------------------------
-- Associations n,n (attributs portes inclus)
-- ---------------------------------------------------------------------------

-- PRENDRE : Patient (1,n) -- Medicament (0,n)
CREATE TABLE Prendre (
  idfPatient       TEXT         NOT NULL,
  idfMedic         INTEGER      NOT NULL,
  datePrise        TEXT         NOT NULL,
  posologie        INTEGER      NOT NULL,
  duree            INTEGER      NOT NULL,
  PRIMARY KEY (idfPatient, idfMedic, datePrise),
  FOREIGN KEY (idfPatient) REFERENCES Patients(idfPatient),
  FOREIGN KEY (idfMedic)   REFERENCES Medicaments(idfMedic)
);

-- COMPOSER : Medicament (0,n) -- Substance (1,n)
CREATE TABLE Composer (
  idfMedic         INTEGER      NOT NULL,
  idfSubstance     TEXT         NOT NULL,
  dosage           TEXT,
  refDosage        TEXT,
  natureComposant  TEXT,
  elementPharma    TEXT,
  numeroLien       TEXT         NOT NULL DEFAULT '1',
  PRIMARY KEY (idfMedic, idfSubstance, numeroLien),
  FOREIGN KEY (idfMedic)     REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfSubstance) REFERENCES Substances(idfSubstance)
);

-- APPARTENIR : Medicament (0,n) -- Groupe (1,n)
CREATE TABLE Appartenir (
  idfMedic         INTEGER      NOT NULL,
  idfGroupe        INTEGER      NOT NULL,
  typeGenerique    INTEGER,
  numeroTri        INTEGER,
  PRIMARY KEY (idfMedic, idfGroupe),
  FOREIGN KEY (idfMedic)  REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfGroupe) REFERENCES Groupes(idfGroupe)
);

-- DETENIR : Laboratoire (1,n) -- Medicament (1,n)
CREATE TABLE Detenir (
  idfLabo          INTEGER      NOT NULL,
  idfMedic         INTEGER      NOT NULL,
  PRIMARY KEY (idfLabo, idfMedic),
  FOREIGN KEY (idfLabo)  REFERENCES Laboratoires(idfLabo),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

-- ---------------------------------------------------------------------------
-- Index utiles (jointures / coherence)
-- ---------------------------------------------------------------------------
CREATE INDEX idx_presentations_medic ON Presentations(idfMedic);
CREATE INDEX idx_prendre_medic       ON Prendre(idfMedic);
CREATE INDEX idx_composer_substance  ON Composer(idfSubstance);
CREATE INDEX idx_appartenir_groupe   ON Appartenir(idfGroupe);
CREATE INDEX idx_detenir_medic       ON Detenir(idfMedic);
