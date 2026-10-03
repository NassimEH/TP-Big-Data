-- TP1 Q2 - DDL pour retroconception Looping
-- Genere le MCD cible (entites + associations)

CREATE TABLE Laboratoires (
  idfLabo INTEGER PRIMARY KEY,
  nom VARCHAR(100) NOT NULL
);

CREATE TABLE Medicaments (
  idfMedic INTEGER PRIMARY KEY,
  denomination VARCHAR(255) NOT NULL,
  forme VARCHAR(100),
  statutAMM VARCHAR(100),
  dateAMM DATE,
  noautorisation VARCHAR(100)
);

CREATE TABLE Patients (
  idfPatient VARCHAR(50) PRIMARY KEY,
  prenom VARCHAR(100),
  nom VARCHAR(100),
  age INTEGER,
  genre VARCHAR(50),
  mail VARCHAR(255)
);

CREATE TABLE Presentations (
  idfPresentation VARCHAR(20) PRIMARY KEY,
  libelle VARCHAR(255),
  statutADM VARCHAR(100),
  dateCom DATE,
  tauxRembt VARCHAR(50),
  prixMedic DECIMAL(10,2),
  prixPublic DECIMAL(10,2),
  idfMedic INTEGER NOT NULL,
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

CREATE TABLE Substances (
  idfSubstance VARCHAR(20) PRIMARY KEY,
  denomination VARCHAR(255) NOT NULL,
  dosage VARCHAR(100),
  refDosage VARCHAR(100)
);

CREATE TABLE Groupes (
  idfGroupe INTEGER PRIMARY KEY,
  libelle VARCHAR(255) NOT NULL
);

-- Association PRENDRE (Patient N-N Medicament)
CREATE TABLE Prendre (
  idfPatient VARCHAR(50) NOT NULL,
  idfMedic INTEGER NOT NULL,
  datePrise DATE NOT NULL,
  posologie INTEGER NOT NULL,
  duree INTEGER NOT NULL,
  PRIMARY KEY (idfPatient, idfMedic, datePrise),
  FOREIGN KEY (idfPatient) REFERENCES Patients(idfPatient),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);

-- Association COMPOSER (Medicament N-N Substance)
CREATE TABLE Composer (
  idfMedic INTEGER NOT NULL,
  idfSubstance VARCHAR(20) NOT NULL,
  dosage VARCHAR(100),
  refDosage VARCHAR(100),
  natureComposant VARCHAR(10),
  elementPharma VARCHAR(100),
  numeroLien VARCHAR(20),
  PRIMARY KEY (idfMedic, idfSubstance, numeroLien),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfSubstance) REFERENCES Substances(idfSubstance)
);

-- Association APPARTENIR (Medicament N-N Groupe)
CREATE TABLE Appartenir (
  idfMedic INTEGER NOT NULL,
  idfGroupe INTEGER NOT NULL,
  typeGenerique INTEGER,
  numeroTri INTEGER,
  PRIMARY KEY (idfMedic, idfGroupe),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic),
  FOREIGN KEY (idfGroupe) REFERENCES Groupes(idfGroupe)
);

-- Association DETENIR (Laboratoire N-N Medicament)
CREATE TABLE Detenir (
  idfLabo INTEGER NOT NULL,
  idfMedic INTEGER NOT NULL,
  PRIMARY KEY (idfLabo, idfMedic),
  FOREIGN KEY (idfLabo) REFERENCES Laboratoires(idfLabo),
  FOREIGN KEY (idfMedic) REFERENCES Medicaments(idfMedic)
);
