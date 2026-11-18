"""Génère une maquette du rapport Power BI (rendu visé) à partir des données."""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

df = pd.read_csv("../data/employes.csv", parse_dates=["date_embauche"])
act = df[df.statut == "Actif"]
BG, CARD, TXT, MUTED, ACC = "#F3F4F8", "#FFFFFF", "#1F2430", "#6B7280", "#2B5BD7"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#D5D9E2",
                     "axes.labelcolor": TXT, "xtick.color": MUTED, "ytick.color": MUTED})

fig = plt.figure(figsize=(16, 9), facecolor=BG)
fig.text(0.02, 0.95, "HR Analytics Dashboard", fontsize=24, weight="bold", color=TXT)
fig.text(0.02, 0.915, "Effectifs, rémunération et rétention — 1 000 employés (données fictives)", fontsize=11, color=MUTED)

def card(x, y, w, h):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, fc=CARD, ec="#E3E6ED", lw=1, zorder=-10))

# Slicers
card(0.02, 0.05, 0.13, 0.80)
fig.text(0.03, 0.82, "Filtres", fontsize=13, weight="bold", color=TXT)
y = 0.77
for title, items in [("Département", ["Tous", "IT", "Ventes", "Finance", "…"]),
                     ("Ville", ["Toutes", "Paris", "Lyon", "Marseille", "…"]),
                     ("Genre", ["Tous", "F", "H"])]:
    fig.text(0.03, y, title, fontsize=10, weight="bold", color=MUTED); y -= 0.035
    for i, it in enumerate(items):
        fig.text(0.035, y, ("■ " if i == 0 else "□ ") + it, fontsize=9.5, color=ACC if i == 0 else TXT); y -= 0.03
    y -= 0.02

# KPI cards
kpis = [("Effectif actif", f"{len(act):,}".replace(",", " ")),
        ("Taux de turnover", f"{(df.statut == 'Parti').mean():.1%}".replace(".", ",")),
        ("Salaire moyen", f"{act.salaire_annuel.mean() / 1000:.1f} k€".replace(".", ",")),
        ("Satisfaction", f"{act.satisfaction.mean():.2f} / 5".replace(".", ",")),
        ("% Femmes", f"{(act.genre == 'F').mean():.1%}".replace(".", ","))]
for i, (lab, val) in enumerate(kpis):
    x = 0.165 + i * 0.165
    card(x, 0.74, 0.155, 0.11)
    fig.text(x + 0.012, 0.815, lab, fontsize=10.5, color=MUTED)
    fig.text(x + 0.012, 0.76, val, fontsize=22, weight="bold", color=TXT)

def panel(rect, title, left=0.035):
    card(*rect)
    ax = fig.add_axes([rect[0] + left, rect[1] + 0.04, rect[2] - left - 0.015, rect[3] - 0.1])
    fig.text(rect[0] + 0.012, rect[1] + rect[3] - 0.035, title, fontsize=12, weight="bold", color=TXT)
    ax.set_facecolor(CARD)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    return ax

# Embauches par année
ax = panel((0.165, 0.39, 0.40, 0.33), "Embauches par année")
h = df.groupby(df.date_embauche.dt.year).size().loc[2012:2026]
ax.plot(h.index, h.values, color=ACC, lw=2.5, marker="o", ms=4)
ax.fill_between(h.index, h.values, color=ACC, alpha=0.08)
ax.grid(axis="y", color="#EEF0F4")

# Turnover par département
ax = panel((0.575, 0.39, 0.405, 0.33), "Taux de turnover par département")
t = df.groupby("departement").statut.apply(lambda s: (s == "Parti").mean()).sort_values(ascending=False)
cols = ["#C0392B" if v >= .2 else "#E67E22" if v >= .15 else "#1E8449" for v in t.values]
bars = ax.bar(range(len(t)), t.values, color=cols, width=0.6)
ax.set_xticks(range(len(t)), [d.replace(" ", "\n") for d in t.index], fontsize=9)
ax.bar_label(bars, labels=[f"{v:.0%}" for v in t.values], fontsize=9, color=TXT)
ax.set_yticks([])
ax.spines["left"].set_visible(False)

# Salaire moyen par poste
ax = panel((0.165, 0.05, 0.27, 0.32), "Salaire moyen par poste", left=0.06)
s = act.groupby("poste").salaire_annuel.mean().reindex(["Junior", "Confirmé", "Senior", "Manager"])
b = ax.barh(s.index, s.values / 1000, color=ACC, height=0.55)
ax.bar_label(b, labels=[f"{v / 1000:.0f} k€" for v in s.values], fontsize=9, padding=3)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)

# Anneau par ville
ax = panel((0.445, 0.05, 0.25, 0.32), "Effectif actif par ville", left=0.0)
v = act.ville.value_counts()
pal = ["#2B5BD7", "#5B8DEF", "#8FB3F5", "#F2994A", "#27AE60", "#9B51E0", "#BDC3CF"]
ax.pie(v.values, colors=pal, startangle=90, wedgeprops=dict(width=0.35, edgecolor="white"))
ax.text(0, 0, f"{len(act)}", ha="center", va="center", fontsize=16, weight="bold", color=TXT)
ax.legend(v.index, loc="center left", bbox_to_anchor=(0.95, 0.5), frameon=False, fontsize=8.5)

# Satisfaction vs départs
ax = panel((0.705, 0.05, 0.275, 0.32), "Turnover selon la satisfaction")
sat = df.groupby("satisfaction").statut.apply(lambda s: (s == "Parti").mean())
b = ax.bar([f"{i}/5" for i in sat.index], sat.values, color="#E67E22", width=0.55)
ax.bar_label(b, labels=[f"{x:.0%}" for x in sat.values], fontsize=9)
ax.set_yticks([])
ax.spines["left"].set_visible(False)

fig.savefig("apercu_maquette.png", dpi=110, facecolor=BG)
print("ok")
