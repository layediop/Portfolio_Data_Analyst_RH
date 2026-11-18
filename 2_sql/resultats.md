# Résultats des requêtes SQL

_Exécutées sur SQLite — 1 000 employés fictifs._


## Q1. Vue d'ensemble : effectif, départs et taux de turnover

```sql
-- Q1. Vue d'ensemble : effectif, départs et taux de turnover
SELECT
    COUNT(*)                                                    AS total_employes,
    SUM(CASE WHEN statut = 'Actif' THEN 1 ELSE 0 END)           AS effectif_actif,
    SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END)           AS departs,
    ROUND(100.0 * SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END) / COUNT(*), 1) AS turnover_pct
FROM employes;
```

|   total_employes |   effectif_actif |   departs |   turnover_pct |
|-----------------:|-----------------:|----------:|---------------:|
|             1000 |              817 |       183 |           18.3 |


## Q2. Turnover et salaire moyen par département (classés par turnover)

```sql
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
```

| departement    |   employes |   departs |   turnover_pct |   salaire_moyen |
|:---------------|-----------:|----------:|---------------:|----------------:|
| Ventes         |        202 |        50 |           24.8 |           46213 |
| Support Client |         98 |        20 |           20.4 |           35051 |
| Opérations     |        233 |        44 |           18.9 |           39187 |
| IT             |        200 |        37 |           18.5 |           57687 |
| Marketing      |        101 |        18 |           17.8 |           47643 |
| RH             |         66 |         8 |           12.1 |           48806 |
| Finance        |        100 |         6 |            6   |           58348 |


## Q3. Jointure : coût de formation par employé actif et par pôle

```sql
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
```

| pole       | departement    |   effectif_actif |   budget_formation |   budget_par_employe |   heures_formation_moy |
|:-----------|:---------------|-----------------:|-------------------:|---------------------:|-----------------------:|
| Commercial | Ventes         |              152 |              90000 |                  592 |                   21   |
| Commercial | Marketing      |               83 |              45000 |                  542 |                   20.2 |
| Production | Support Client |               78 |              30000 |                  385 |                   22.7 |
| Production | Opérations     |              189 |              70000 |                  370 |                   22.1 |
| Support    | IT             |              163 |             120000 |                  736 |                   20.9 |
| Support    | RH             |               58 |              25000 |                  431 |                   20.9 |
| Support    | Finance        |               94 |              40000 |                  426 |                   22.7 |


## Q4. Écart salarial femmes / hommes par poste

```sql
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
```

| poste    |   salaire_moyen_f |   salaire_moyen_h |   ecart_pct |
|:---------|------------------:|------------------:|------------:|
| Junior   |             38472 |             37518 |        -2.5 |
| Confirmé |             44749 |             44999 |         0.6 |
| Senior   |             55742 |             58374 |         4.5 |
| Manager  |             73286 |             74471 |         1.6 |


## Q5. Lien satisfaction ↔ départs (le facteur clé de rétention)

```sql
-- Q5. Lien satisfaction ↔ départs (le facteur clé de rétention)
SELECT
    satisfaction,
    COUNT(*)                                                    AS employes,
    ROUND(100.0 * SUM(CASE WHEN statut = 'Parti' THEN 1 ELSE 0 END) / COUNT(*), 1) AS turnover_pct,
    ROUND(AVG(jours_absence), 1)                                AS absences_moy
FROM employes
GROUP BY satisfaction
ORDER BY satisfaction;
```

|   satisfaction |   employes |   turnover_pct |   absences_moy |
|---------------:|-----------:|---------------:|---------------:|
|              1 |         23 |           30.4 |            9.3 |
|              2 |        166 |           24.7 |            8.6 |
|              3 |        355 |           16.3 |            8   |
|              4 |        319 |           17.9 |            7.2 |
|              5 |        137 |           14.6 |            6.3 |


## Q6. CTE + fenêtre : top 3 des salaires par département (employés actifs)

```sql
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
```

| departement    |   rang | nom             | poste   |   salaire_annuel |
|:---------------|-------:|:----------------|:--------|-----------------:|
| Finance        |      1 | Léa Petit       | Manager |           106600 |
| Finance        |      2 | Louis Martin    | Manager |            97500 |
| Finance        |      3 | Karim Roux      | Manager |            93000 |
| IT             |      1 | Chloé Mercier   | Senior  |            97300 |
| IT             |      2 | Nathan Fall     | Manager |            97100 |
| IT             |      3 | Sarah Girard    | Manager |            92200 |
| Marketing      |      1 | Nathan Haddad   | Manager |            93700 |
| Marketing      |      2 | Sarah Petit     | Manager |            89800 |
| Marketing      |      3 | Léa Roux        | Manager |            82300 |
| Opérations     |      1 | Léa Moreau      | Manager |            76200 |
| Opérations     |      2 | Hugo Fournier   | Manager |            71700 |
| Opérations     |      3 | Adam Sow        | Manager |            69600 |
| RH             |      1 | Aïcha Fournier  | Manager |            85100 |
| RH             |      2 | Lucas Diop      | Manager |            72800 |
| RH             |      3 | Adam Diop       | Senior  |            72000 |
| Support Client |      1 | Camille Laurent | Manager |            59600 |
| Support Client |      2 | Nathan Moreau   | Manager |            58200 |
| Support Client |      3 | Thomas Fournier | Manager |            54700 |
| Support Client |      3 | Lucas Petit     | Manager |            54700 |
| Ventes         |      1 | Emma Laurent    | Manager |            82200 |
| Ventes         |      2 | Nathan Petit    | Manager |            80500 |
| Ventes         |      3 | Hugo Dubois     | Manager |            77700 |


## Q7. Fenêtre : embauches par année et cumul de l'effectif recruté

```sql
-- Q7. Fenêtre : embauches par année et cumul de l'effectif recruté
SELECT
    CAST(strftime('%Y', date_embauche) AS INTEGER)              AS annee,   -- PostgreSQL : EXTRACT(YEAR FROM date_embauche)
    COUNT(*)                                                    AS embauches,
    SUM(COUNT(*)) OVER (ORDER BY CAST(strftime('%Y', date_embauche) AS INTEGER)) AS cumul
FROM employes
GROUP BY annee
ORDER BY annee;
```

|   annee |   embauches |   cumul |
|--------:|------------:|--------:|
|    2008 |           6 |       6 |
|    2009 |          22 |      28 |
|    2010 |          27 |      55 |
|    2011 |          33 |      88 |
|    2012 |          20 |     108 |
|    2013 |          32 |     140 |
|    2014 |          40 |     180 |
|    2015 |          42 |     222 |
|    2016 |          43 |     265 |
|    2017 |          44 |     309 |
|    2018 |          61 |     370 |
|    2019 |          60 |     430 |
|    2020 |          64 |     494 |
|    2021 |          79 |     573 |
|    2022 |          56 |     629 |
|    2023 |          91 |     720 |
|    2024 |          93 |     813 |
|    2025 |          77 |     890 |
|    2026 |         110 |    1000 |


## Q8. Employés « à risque » : actifs, peu satisfaits, très absents, bien notés

```sql
-- Q8. Employés « à risque » : actifs, peu satisfaits, très absents, bien notés
--     (talents à retenir en priorité)
SELECT id_employe, nom, departement, poste, note_performance, satisfaction, jours_absence
FROM employes
WHERE statut = 'Actif'
  AND satisfaction <= 2
  AND note_performance >= 4
ORDER BY jours_absence DESC
LIMIT 10;
```

| id_employe   | nom            | departement    | poste    |   note_performance |   satisfaction |   jours_absence |
|:-------------|:---------------|:---------------|:---------|-------------------:|---------------:|----------------:|
| E0281        | Hugo Fournier  | IT             | Senior   |                  4 |              2 |              18 |
| E0095        | Aïcha Petit    | Ventes         | Confirmé |                  5 |              2 |              15 |
| E0720        | Emma Mercier   | Support Client | Senior   |                  4 |              2 |              15 |
| E0124        | Yanis Martin   | Marketing      | Confirmé |                  4 |              1 |              14 |
| E0240        | Inès Garcia    | IT             | Junior   |                  5 |              2 |              14 |
| E0512        | Manon Laurent  | Opérations     | Confirmé |                  4 |              2 |              14 |
| E0724        | Nathan Laurent | Support Client | Confirmé |                  4 |              2 |              14 |
| E0248        | Louis Petit    | Marketing      | Senior   |                  4 |              2 |              13 |
| E0454        | Mamadou Roux   | IT             | Confirmé |                  4 |              2 |              13 |
| E0604        | Camille Ba     | Opérations     | Junior   |                  5 |              1 |              13 |
