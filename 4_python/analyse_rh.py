"""
Projet 4 : Analyse RH avec Python
- Nettoyage et enrichissement des données (pandas)
- Analyse exploratoire : turnover, salaires, satisfaction, ancienneté
- Visualisations (matplotlib)
- Génération d'un rapport PDF (reportlab)

Usage : python analyse_rh.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DATA = Path(__file__).parent.parent / "data" / "employes.csv"
FIG = Path(__file__).parent / "figures"
FIG.mkdir(exist_ok=True)
REF = pd.Timestamp("2026-09-30")
BLUE, RED, ORANGE, GREEN, GREY = "#2B5BD7", "#C0392B", "#E67E22", "#1E8449", "#6B7280"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12})

# ------------------------------------------------------------------
# 1. Chargement et nettoyage
# ------------------------------------------------------------------
df = pd.read_csv(DATA, parse_dates=["date_embauche", "date_depart"])
n_brut = len(df)
df = df.drop_duplicates("id_employe")
df = df[df["salaire_annuel"] > 0]
for col in ["departement", "poste", "ville", "statut"]:
    df[col] = df[col].str.strip()

# Variables dérivées
fin = df["date_depart"].fillna(REF)
df["anciennete_ans"] = ((fin - df["date_embauche"]).dt.days / 365.25).round(1)
df["parti"] = (df["statut"] == "Parti").astype(int)
df["tranche_age"] = pd.cut(df["age"], [20, 29, 39, 49, 64], labels=["20-29", "30-39", "40-49", "50+"])
df["tranche_anciennete"] = pd.cut(df["anciennete_ans"], [-0.1, 1, 3, 5, 10, 30],
                                  labels=["< 1 an", "1-3 ans", "3-5 ans", "5-10 ans", "10+ ans"])
actifs = df[df["statut"] == "Actif"]
print(f"{n_brut} lignes chargées, {len(df)} après nettoyage, {len(actifs)} actifs")

# ------------------------------------------------------------------
# 2. Indicateurs clés
# ------------------------------------------------------------------
kpi = {
    "Effectif actif": f"{len(actifs)}",
    "Taux de turnover": f"{df['parti'].mean():.1%}",
    "Salaire moyen (actifs)": f"{actifs['salaire_annuel'].mean():,.0f} €".replace(",", " "),
    "Masse salariale annuelle": f"{actifs['salaire_annuel'].sum() / 1e6:.1f} M€",
    "Satisfaction moyenne": f"{actifs['satisfaction'].mean():.2f} / 5",
    "Ancienneté moyenne": f"{actifs['anciennete_ans'].mean():.1f} ans",
}

par_dept = (df.groupby("departement")
              .agg(employes=("id_employe", "count"), turnover=("parti", "mean"),
                   salaire_moyen=("salaire_annuel", "mean"), satisfaction=("satisfaction", "mean"))
              .sort_values("turnover", ascending=False))
turn_sat = df.groupby("satisfaction")["parti"].mean()
turn_anc = df.groupby("tranche_anciennete", observed=True)["parti"].mean()
corr = df[["salaire_annuel", "age", "anciennete_ans", "note_performance", "satisfaction",
           "heures_formation", "jours_absence", "parti"]].corr()["parti"].drop("parti").sort_values()

# ------------------------------------------------------------------
# 3. Visualisations
# ------------------------------------------------------------------
def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=160)
    plt.close(fig)

# 3.1 Turnover par département
fig, ax = plt.subplots(figsize=(8, 4))
t = par_dept["turnover"].sort_values()
c = [RED if v >= .2 else ORANGE if v >= .15 else GREEN for v in t]
b = ax.barh(t.index, t.values, color=c)
ax.bar_label(b, labels=[f"{v:.1%}" for v in t], padding=3)
ax.axvline(df["parti"].mean(), color=GREY, ls="--", lw=1)
ax.text(df["parti"].mean(), -0.9, " moyenne", color=GREY, fontsize=9)
ax.set_xlim(0, t.max() * 1.18)
ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
ax.set_title("Taux de turnover par département")
save(fig, "01_turnover_departement.png")

# 3.2 Turnover selon la satisfaction
fig, ax = plt.subplots(figsize=(8, 4))
b = ax.bar([f"{i}/5" for i in turn_sat.index], turn_sat.values, color=ORANGE, width=0.6)
ax.bar_label(b, labels=[f"{v:.0%}" for v in turn_sat], padding=2)
ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
ax.set_xlabel("Note de satisfaction")
ax.set_title("Plus la satisfaction est basse, plus les départs sont fréquents")
save(fig, "02_turnover_satisfaction.png")

# 3.3 Distribution des salaires par poste
fig, ax = plt.subplots(figsize=(8, 4))
postes = ["Junior", "Confirmé", "Senior", "Manager"]
bp = ax.boxplot([actifs.loc[actifs.poste == p, "salaire_annuel"] / 1000 for p in postes],
                tick_labels=postes, patch_artist=True, widths=0.5,
                medianprops=dict(color="white", lw=2))
for patch in bp["boxes"]:
    patch.set_facecolor(BLUE)
ax.set_ylabel("Salaire annuel (k€)")
ax.set_title("Distribution des salaires par poste (employés actifs)")
save(fig, "03_salaires_poste.png")

# 3.4 Turnover selon l'ancienneté
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(turn_anc.index.astype(str), turn_anc.values, color=BLUE, marker="o", lw=2.5)
for x, y in zip(turn_anc.index.astype(str), turn_anc.values):
    ax.annotate(f"{y:.0%}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")
ax.set_ylim(0, turn_anc.max() * 1.25)
ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
ax.set_title("Taux de départ selon l'ancienneté")
save(fig, "04_turnover_anciennete.png")

# 3.5 Corrélations avec le départ
fig, ax = plt.subplots(figsize=(8, 4))
c = [RED if v > 0 else GREEN for v in corr]
ax.barh(corr.index, corr.values, color=c)
ax.axvline(0, color=GREY, lw=0.8)
ax.set_title("Corrélation de chaque variable avec le départ")
ax.set_xlabel("Coefficient de corrélation (Pearson)")
save(fig, "05_correlations.png")

# 3.6 Effectif actif par ville
fig, ax = plt.subplots(figsize=(8, 4))
v = actifs["ville"].value_counts().sort_values()
b = ax.barh(v.index, v.values, color=BLUE)
ax.bar_label(b, padding=3)
ax.set_title("Effectif actif par ville")
save(fig, "06_effectif_ville.png")

# ------------------------------------------------------------------
# 4. Rapport PDF
# ------------------------------------------------------------------
pire, meilleur = par_dept.index[0], par_dept.index[-1]
ratio_sat = turn_sat.iloc[0] / turn_sat.iloc[-1]
insights = [
    f"Le turnover global atteint <b>{df['parti'].mean():.1%}</b> sur la période ; il est le plus élevé en "
    f"<b>{pire} ({par_dept.turnover.iloc[0]:.1%})</b> et le plus bas en <b>{meilleur} "
    f"({par_dept.turnover.iloc[-1]:.1%})</b>.",
    f"La satisfaction est le premier signal d'alerte : les employés notés 1/5 partent "
    f"<b>{ratio_sat:.1f} fois plus</b> que ceux notés 5/5.",
    f"Les absences sont liées au mal-être : {df[df.satisfaction <= 2].jours_absence.mean():.1f} jours en moyenne "
    f"pour les peu satisfaits contre {df[df.satisfaction >= 4].jours_absence.mean():.1f} pour les satisfaits.",
    f"Les premières années sont critiques : le taux de départ est de <b>{turn_anc.iloc[0]:.0%}</b> "
    f"pour les employés de moins d'un an.",
]
reco = [
    "Lancer un plan de rétention ciblé sur les Ventes et le Support Client (entretiens, primes, parcours).",
    "Mettre en place un baromètre de satisfaction trimestriel et suivre les scores ≤ 2 comme alerte RH.",
    "Renforcer l'onboarding la première année (parrainage, points d'étape à 3, 6 et 12 mois).",
    "Suivre les talents à risque : performance ≥ 4 et satisfaction ≤ 2.",
]

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], textColor=colors.HexColor("#1F2430"), fontSize=22)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor(BLUE), spaceBefore=10)
P = ParagraphStyle("P", parent=styles["BodyText"], fontSize=10, leading=14)

story = [Paragraph("Rapport d'analyse RH 2026", H1),
         Paragraph("Effectifs, rémunération et rétention — 1 000 employés (données fictives)", P),
         Spacer(1, 12), Paragraph("Indicateurs clés", H2)]
kt = Table([[k, v] for k, v in kpi.items()], colWidths=[8 * cm, 6 * cm])
kt.setStyle(TableStyle([("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#F3F5FA"), colors.white]),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D9E2")),
                        ("PADDING", (0, 0), (-1, -1), 6)]))
story += [kt, Paragraph("Principaux enseignements", H2)]
story += [Paragraph("• " + s, P) for s in insights]
story += [Paragraph("Recommandations", H2)] + [Paragraph(f"{i}. {r}", P) for i, r in enumerate(reco, 1)]

story += [PageBreak(), Paragraph("Analyse par département", H2)]
rows = [["Département", "Employés", "Turnover", "Salaire moyen", "Satisfaction"]]
for d, r in par_dept.iterrows():
    rows.append([d, int(r.employes), f"{r.turnover:.1%}", f"{r.salaire_moyen:,.0f} €".replace(",", " "),
                 f"{r.satisfaction:.2f}"])
dt = Table(rows, colWidths=[4 * cm, 2.5 * cm, 2.5 * cm, 3.5 * cm, 2.5 * cm])
dt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BLUE)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F5FA")]),
                        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                        ("PADDING", (0, 0), (-1, -1), 5)]))
story += [dt, Spacer(1, 10)]
for name in sorted(FIG.glob("*.png")):
    story.append(Image(str(name), width=16 * cm, height=8 * cm))
    story.append(Spacer(1, 6))

SimpleDocTemplate(str(Path(__file__).parent / "Rapport_Analyse_RH.pdf"), pagesize=A4,
                  leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="Rapport d'analyse RH 2026").build(story)
print("Rapport généré : Rapport_Analyse_RH.pdf")
for s in insights:
    print("-", s.replace("<b>", "").replace("</b>", ""))
