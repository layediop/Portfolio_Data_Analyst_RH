-- =============================================================
-- Projet 2 : Analyse RH en SQL — Schéma de la base
-- Compatible SQLite / PostgreSQL / MySQL (types standards)
-- =============================================================

DROP TABLE IF EXISTS employes;
DROP TABLE IF EXISTS departements;

-- Table de référence des départements (budget et responsable)
CREATE TABLE departements (
    departement     VARCHAR(30) PRIMARY KEY,
    pole            VARCHAR(30) NOT NULL,
    budget_formation INTEGER    NOT NULL   -- budget annuel de formation en €
);

INSERT INTO departements (departement, pole, budget_formation) VALUES
    ('IT',             'Support',     120000),
    ('Ventes',         'Commercial',   90000),
    ('Marketing',      'Commercial',   45000),
    ('Finance',        'Support',      40000),
    ('RH',             'Support',      25000),
    ('Opérations',     'Production',   70000),
    ('Support Client', 'Production',   30000);

-- Table des employés (chargée depuis data/employes.csv)
CREATE TABLE employes (
    id_employe        VARCHAR(10) PRIMARY KEY,
    nom               VARCHAR(60),
    genre             CHAR(1),
    age               INTEGER,
    departement       VARCHAR(30) REFERENCES departements(departement),
    poste             VARCHAR(20),
    ville             VARCHAR(30),
    date_embauche     DATE,
    salaire_annuel    NUMERIC(10, 2),
    note_performance  INTEGER,
    satisfaction      INTEGER,
    heures_formation  INTEGER,
    jours_absence     INTEGER,
    statut            VARCHAR(10),
    date_depart       DATE
);
