# Projet 3 — Power BI : « HR Analytics Dashboard »

Ce dossier contient tout ce qu'il faut pour construire le rapport dans **Power BI Desktop** (gratuit, Windows) en 30 à 45 minutes, puis l'enregistrer en `HR_Analytics.pbix` et l'ajouter au dépôt GitHub.

`apercu_maquette.png` montre le rendu visé.

---

## Étape 1 — Importer les données

1. *Accueil → Obtenir les données → Texte/CSV* → `data/employes.csv`.
2. Cliquer sur **Transformer les données** (Power Query) et vérifier les types :
   - `date_embauche`, `date_depart` → **Date**
   - `salaire_annuel` → **Nombre décimal**
   - `age`, `note_performance`, `satisfaction`, `heures_formation`, `jours_absence` → **Nombre entier**
3. Renommer la requête en **Employes**, puis *Fermer et appliquer*.

## Étape 2 — Créer la table Calendrier

*Modélisation → Nouvelle table* :

```DAX
Calendrier =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2008, 1, 1 ), DATE ( 2026, 12, 31 ) ),
    "Annee", YEAR ( [Date] ),
    "Mois", FORMAT ( [Date], "mmm" ),
    "NumMois", MONTH ( [Date] )
)
```

Marquer la table comme **table de dates** (clic droit → *Marquer comme table de dates*).

## Étape 3 — Modèle de données (vue Modèle)

| De | Vers | Cardinalité | Statut |
|---|---|---|---|
| `Calendrier[Date]` | `Employes[date_embauche]` | 1 → * | **Active** |
| `Calendrier[Date]` | `Employes[date_depart]` | 1 → * | Inactive (utilisée via `USERELATIONSHIP`) |

## Étape 4 — Mesures DAX

Créer une table vide *Mesures* (Accueil → Entrer des données → nommer « _Mesures ») puis y coller chaque mesure du fichier **`mesures_DAX.dax`**.

Formats : `Taux Turnover`, `Pct Femmes`, `Ecart Salarial F/H` en **%** ; `Salaire Moyen`, `Masse Salariale` en **€**.

## Étape 5 — Visuels (page unique, 16:9)

| Zone | Visuel | Champs |
|---|---|---|
| Bandeau haut | 5 **cartes** | Effectif Actif · Taux Turnover · Salaire Moyen · Satisfaction Moyenne · Pct Femmes |
| Gauche, milieu | **Graphique en courbes** « Embauches par année » | Axe : `Calendrier[Annee]` · Valeur : `Embauches` |
| Droite, milieu | **Histogramme groupé** « Turnover par département » | Axe : `departement` · Valeur : `Taux Turnover` · Couleur : *fx → Valeur du champ → Couleur Turnover* |
| Gauche, bas | **Barres horizontales** « Salaire moyen par poste » | Axe : `poste` · Valeur : `Salaire Moyen` |
| Centre, bas | **Anneau** « Effectif par ville » | Légende : `ville` · Valeur : `Effectif Actif` |
| Droite, bas | **Matrice** « Satisfaction vs départs » | Lignes : `satisfaction` · Valeurs : `Total Employes`, `Taux Turnover` |
| Panneau gauche | 3 **segments** (slicers) | `departement`, `ville`, `genre` |

Conseils de mise en forme : thème sombre ou bleu nuit, police Segoe UI, titres de visuels en gras, coins arrondis à 8 px, ombres légères.

## Étape 6 — Insights à mettre en avant (zone de texte)

- Turnover global de **18,3 %**, avec un pic dans les **Ventes (24,8 %)** et un minimum en **Finance (6 %)**.
- Les employés notés **1/5 en satisfaction** partent deux fois plus (**30 %**) que ceux notés **5/5 (15 %)**.
- L'écart salarial F/H reste faible (< 5 %), le plus marqué au niveau **Senior**.

## Étape 7 — Publier

- *Fichier → Enregistrer sous* → `3_powerbi/HR_Analytics.pbix`
- Exporter un PDF ou une capture du rapport pour le README GitHub.
- Optionnel : *Publier* vers Power BI Service et ajouter le lien « Publier sur le web » au README.
