"""Génère un jeu de données RH fictif et réaliste (1 000 employés)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 1000

depts = {
    # département: (poids, salaire de base annuel €, taux de départ)
    "IT": (0.18, 52000, 0.17),
    "Ventes": (0.22, 40000, 0.24),
    "Marketing": (0.10, 43000, 0.19),
    "Finance": (0.10, 50000, 0.11),
    "RH": (0.07, 41000, 0.12),
    "Opérations": (0.23, 34000, 0.21),
    "Support Client": (0.10, 31000, 0.27),
}
postes = {"Junior": 0.85, "Confirmé": 1.0, "Senior": 1.3, "Manager": 1.65}
villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Lille", "Nantes", "Bordeaux"]
ville_poids = [0.34, 0.16, 0.12, 0.11, 0.10, 0.09, 0.08]
prenoms_f = ["Emma", "Léa", "Chloé", "Fatou", "Inès", "Sarah", "Camille", "Aïcha", "Manon", "Julie"]
prenoms_h = ["Lucas", "Hugo", "Mamadou", "Yanis", "Thomas", "Karim", "Louis", "Moussa", "Nathan", "Adam"]
noms = ["Martin", "Bernard", "Diop", "Dubois", "Ndiaye", "Moreau", "Benali", "Laurent", "Fall", "Garcia",
        "Petit", "Sow", "Roux", "Haddad", "Fournier", "Ba", "Girard", "Mercier"]

dept_names = list(depts)
dept_col = rng.choice(dept_names, N, p=[d[0] for d in depts.values()])
rows = []
ref = pd.Timestamp("2026-09-30")
for i, d in enumerate(dept_col):
    _, base, quit_rate = depts[d]
    genre = rng.choice(["F", "H"], p=[0.47, 0.53])
    prenom = rng.choice(prenoms_f if genre == "F" else prenoms_h)
    age = int(np.clip(rng.normal(37, 9), 21, 63))
    poste = rng.choice(list(postes), p=[0.32, 0.36, 0.22, 0.10])
    anciennete_max = max(0.3, age - 21)
    embauche = ref - pd.Timedelta(days=int(rng.uniform(0.2, min(anciennete_max, 18)) * 365))
    salaire = base * postes[poste] * rng.normal(1, 0.08) * (1 + 0.01 * (ref - embauche).days / 365)
    perf = int(np.clip(round(rng.normal(3.4, 0.9)), 1, 5))
    satisfaction = int(np.clip(round(rng.normal(3.5, 1.0)), 1, 5))
    formation_h = int(max(0, rng.normal(22, 12)))
    absences = int(max(0, rng.poisson(6) + (5 - satisfaction) * rng.integers(0, 3)))
    # probabilité de départ influencée par satisfaction et poste
    p_quit = quit_rate * (1.6 - 0.2 * satisfaction) * (1.2 if poste == "Junior" else 0.9)
    parti = rng.random() < p_quit
    date_depart = pd.NaT
    if parti:
        date_depart = embauche + (ref - embauche) * rng.uniform(0.3, 1)
        date_depart = max(date_depart, ref - pd.Timedelta(days=730))  # départs sur 2 ans
    rows.append({
        "id_employe": f"E{i + 1:04d}",
        "nom": f"{prenom} {rng.choice(noms)}",
        "genre": genre,
        "age": age,
        "departement": d,
        "poste": poste,
        "ville": rng.choice(villes, p=ville_poids),
        "date_embauche": embauche.date(),
        "salaire_annuel": round(salaire, -2),
        "note_performance": perf,
        "satisfaction": satisfaction,
        "heures_formation": formation_h,
        "jours_absence": absences,
        "statut": "Parti" if parti else "Actif",
        "date_depart": date_depart.date() if parti else None,
    })

df = pd.DataFrame(rows)
df.to_csv("employes.csv", index=False, encoding="utf-8")
print(df.shape, df["statut"].value_counts().to_dict())
print(df.groupby("departement")["salaire_annuel"].mean().round())
