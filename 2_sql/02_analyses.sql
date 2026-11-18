-- =============================================================
-- Projet 2 : Analyse RH en SQL — Requêtes d'analyse
-- Notions : agrégations, CASE, jointures, CTE, fonctions de fenêtre
-- =============================================================

-- Q1. Vue d'ensemble : effectif, départs et taux de turnover
SELECT
    COUNT(*)                                                    AS total_employes,
    SUM(CASE WHEN statut = 'Actif' THEN 1 ELSE 0 END)           AS effectif_actif,
    SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END)           AS departs,
    ROUND(100.0 * SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END) / COUNT(*), 1) AS turnover_pct
FROM employes;

-- Q2. Turnover et salaire moyen par département (classés par turnover)
SELECT
    departement,
    COUNT(*)                                                    AS employes,
    SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END)           AS departs,
    ROUND(100.0 * SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END) / COUNT(*), 1) AS turnover_pct,
    ROUND(AVG(salaire_annuel), 0)                               AS salaire_moyen
FROM employes
GROUP BY departement
ORDER BY turnover_pct DESC;

-- Q3. Jointure : coût de formation par employé actif et par pôle
SELECT
    d.pole,
    d.departement,
    COUNT(e.id_employe)                                         AS effectif_actif,
    d.budget_formation,
    ROUND(1.0 * d.budget_formation / COUNT(e.id_employe), 0)    AS budget_par_employe,
    ROUND(AVG(e.heures_formation), 1)                           AS heures_formation_moy
FROM departements d
JOIN employes e ON e.departement = d.departement
WHERE e.statut = 'Actif'
GROUP BY d.pole, d.departement, d.budget_formation
ORDER BY d.pole, budget_par_employe DESC;

-- Q4. Écart salarial femmes / hommes par poste
SELECT
    poste,
    ROUND(AVG(CASE WHEN genre = 'F' THEN salaire_annuel END), 0) AS salaire_moyen_f,
    ROUND(AVG(CASE WHEN genre = 'H' THEN salaire_annuel END), 0) AS salaire_moyen_h,
    ROUND(100.0 * (AVG(CASE WHEN genre = 'H' THEN salaire_annuel END)
                 - AVG(CASE WHEN genre = 'F' THEN salaire_annuel END))
                 / AVG(CASE WHEN genre = 'H' THEN salaire_annuel END), 1) AS ecart_pct
FROM employes
WHERE statut = 'Actif'
GROUP BY poste
ORDER BY salaire_moyen_h;

-- Q5. Lien satisfaction ↔ départs (le facteur clé de rétention)
SELECT
    satisfaction,
    COUNT(*)                                                    AS employes,
    ROUND(100.0 * SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END) / COUNT(*), 1) AS turnover_pct,
    ROUND(AVG(jours_absence), 1)                                AS absences_moy
FROM employes
GROUP BY satisfaction
ORDER BY satisfaction;

-- Q6. CTE + fenêtre : top 3 des salaires par département (employés actifs)
WITH classement AS (
    SELECT
        departement,
        nom,
        poste,
        salaire_annuel,
        RANK() OVER (PARTITION BY departement ORDER BY salaire_annuel DESC) AS rang
    FROM employes
    WHERE statut = 'Actif'
)
SELECT departement, rang, nom, poste, salaire_annuel
FROM classement
WHERE rang <= 3
ORDER BY departement, rang;

-- Q7. Fenêtre : embauches par année et cumul de l'effectif recruté
SELECT
    CAST(strftime('%Y', date_embauche) AS INTEGER)              AS annee,   -- PostgreSQL : EXTRACT(YEAR FROM date_embauche)
    COUNT(*)                                                    AS embauches,
    SUM(COUNT(*)) OVER (ORDER BY CAST(strftime('%Y', date_embauche) AS INTEGER)) AS cumul
FROM employes
GROUP BY annee
ORDER BY annee;

-- Q8. Employés « à risque » : actifs, peu satisfaits, très absents, bien notés
--     (talents à retenir en priorité)
SELECT id_employe, nom, departement, poste, note_performance, satisfaction, jours_absence
FROM employes
WHERE statut = 'Actif'
  AND satisfaction <= 2
  AND note_performance >= 4
ORDER BY jours_absence DESC
LIMIT 10;
