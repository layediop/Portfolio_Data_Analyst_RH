"""Construit le tableau de bord RH Excel (formules dynamiques + graphiques + filtre)."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.comments import Comment

df = pd.read_csv("../data/employes.csv", parse_dates=["date_embauche", "date_depart"])
df["annee_embauche"] = df["date_embauche"].dt.year
N = len(df)
last = N + 1

GREEN = "1E7145"
LIGHT = "E8F5EC"
F = "Arial"
thin = Side(style="thin", color="C9DCCF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()
dash = wb.active
dash.title = "Dashboard"
data = wb.create_sheet("Donnees")
calc = wb.create_sheet("Calculs")

# ---------- Feuille Données ----------
cols = ["id_employe", "nom", "genre", "age", "departement", "poste", "ville", "date_embauche",
        "annee_embauche", "salaire_annuel", "note_performance", "satisfaction",
        "heures_formation", "jours_absence", "statut", "date_depart"]
data.append(cols)
for r in df[cols].itertuples(index=False):
    row = list(r)
    row[7] = row[7].date()
    row[15] = None if pd.isna(row[15]) else row[15].date()
    data.append(row)
for c in range(1, len(cols) + 1):
    data.cell(1, c).font = Font(name=F, bold=True, color="FFFFFF")
    data.column_dimensions[get_column_letter(c)].width = 15
for row in data.iter_rows(min_row=2):
    for cell in row:
        cell.font = Font(name=F, size=10)
    row[7].number_format = "dd/mm/yyyy"
    row[15].number_format = "dd/mm/yyyy"
    row[9].number_format = '#,##0 "€"'
tab = Table(displayName="Employes", ref=f"A1:P{last}")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium7", showRowStripes=True)
data.add_table(tab)
data.freeze_panes = "A2"

# plages nommées utilisées dans les formules
R = {
    "genre": f"Donnees!$C$2:$C${last}", "age": f"Donnees!$D$2:$D${last}",
    "dept": f"Donnees!$E$2:$E${last}", "poste": f"Donnees!$F$2:$F${last}",
    "ville": f"Donnees!$G$2:$G${last}", "annee": f"Donnees!$I$2:$I${last}",
    "sal": f"Donnees!$J$2:$J${last}", "perf": f"Donnees!$K$2:$K${last}",
    "satis": f"Donnees!$L$2:$L${last}", "form": f"Donnees!$M$2:$M${last}",
    "abs": f"Donnees!$N$2:$N${last}", "statut": f"Donnees!$O$2:$O${last}",
}
V = "Dashboard!$C$4"  # critère ville (Toutes -> *)
FV = f'{R["ville"]},{V}'

# ---------- Dashboard ----------
dash.sheet_view.showGridLines = False
for col, w in zip("ABCDEFGHIJKLMNOPQ", [2, 16, 14, 2, 16, 14, 2, 16, 14, 2, 16, 14, 2, 22, 22, 2, 2]):
    dash.column_dimensions[col].width = w

dash.merge_cells("B1:O1")
dash["B1"] = "TABLEAU DE BORD RH — EFFECTIFS, SALAIRES & TURNOVER 2026"
dash["B1"].font = Font(name=F, size=18, bold=True, color="FFFFFF")
dash["B1"].fill = PatternFill("solid", fgColor=GREEN)
dash["B1"].alignment = Alignment(horizontal="center", vertical="center")
dash.row_dimensions[1].height = 36
dash["B2"] = "Données fictives : 1 000 employés, situation au 30/09/2026. Choisissez une ville en C3 pour filtrer tout le tableau."
dash["B2"].font = Font(name=F, size=9, italic=True, color="666666")

dash["B3"] = "Filtre ville ▸"
dash["B3"].font = Font(name=F, bold=True, color=GREEN)
dash["C3"] = "Toutes"
dash["C3"].font = Font(name=F, bold=True)
dash["C3"].fill = PatternFill("solid", fgColor="FFF2CC")
dash["C3"].border = box
dash["C3"].comment = Comment("Cellule à modifier : choisissez une ville dans la liste ou « Toutes ».", "Portfolio")
villes = sorted(df["ville"].unique())
dv = DataValidation(type="list", formula1='"' + ",".join(["Toutes"] + villes) + '"', allow_blank=False)
dash.add_data_validation(dv)
dv.add("C3")
dash["C4"] = '=IF(C3="Toutes","*",C3)'
dash["C4"].font = Font(name=F, color="FFFFFF", size=8)  # cellule technique

# KPI cards
kpis = [
    ("B", "Effectif actif", f'=COUNTIFS({R["statut"]},"Actif",{FV})', "#,##0"),
    ("E", "Taux de turnover", f'=IFERROR(COUNTIFS({R["statut"]},"Parti",{FV})/COUNTIFS({FV}),0)', "0.0%"),
    ("H", "Salaire moyen", f'=IFERROR(AVERAGEIFS({R["sal"]},{R["statut"]},"Actif",{FV}),0)', '#,##0 "€"'),
    ("K", "Satisfaction moy.", f'=IFERROR(AVERAGEIFS({R["satis"]},{R["statut"]},"Actif",{FV}),0)', '0.00 "/5"'),
    ("N", "% Femmes", f'=IFERROR(COUNTIFS({R["genre"]},"F",{R["statut"]},"Actif",{FV})/COUNTIFS({R["statut"]},"Actif",{FV}),0)', "0.0%"),
]
for col, label, formula, fmt in kpis:
    c2 = get_column_letter(dash[col + "1"].column + 1)
    dash.merge_cells(f"{col}6:{c2}6")
    dash.merge_cells(f"{col}7:{c2}8")
    dash[f"{col}6"] = label
    dash[f"{col}6"].font = Font(name=F, size=10, bold=True, color="FFFFFF")
    dash[f"{col}6"].fill = PatternFill("solid", fgColor=GREEN)
    dash[f"{col}6"].alignment = Alignment(horizontal="center")
    dash[f"{col}7"] = formula
    dash[f"{col}7"].number_format = fmt
    dash[f"{col}7"].font = Font(name=F, size=20, bold=True, color=GREEN)
    dash[f"{col}7"].alignment = Alignment(horizontal="center", vertical="center")
    for rr in (6, 7, 8):
        for cc in (col, c2):
            dash[f"{cc}{rr}"].border = box
            if rr > 6:
                dash[f"{cc}{rr}"].fill = PatternFill("solid", fgColor=LIGHT)

# ---------- Calculs (tables sources des graphiques) ----------
def header(ws, row, col, titles):
    for i, t in enumerate(titles):
        c = ws.cell(row, col + i, t)
        c.font = Font(name=F, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=GREEN)
        c.border = box

def body(ws, cell, fmt=None):
    cell.font = Font(name=F, size=10)
    cell.border = box
    if fmt:
        cell.number_format = fmt

calc.column_dimensions["A"].width = 18
for c in "BCDEFGHIJ":
    calc.column_dimensions[c].width = 15
calc["A1"] = "Tables calculées (formules) — alimentent les graphiques du Dashboard et suivent le filtre ville"
calc["A1"].font = Font(name=F, bold=True, size=12, color=GREEN)

# 1. Par département
depts = sorted(df["departement"].unique())
header(calc, 3, 1, ["Département", "Effectif actif", "Départs", "Turnover", "Salaire moyen", "Perf. moy."])
for i, d in enumerate(depts):
    r = 4 + i
    calc.cell(r, 1, d)
    calc.cell(r, 2, f'=COUNTIFS({R["dept"]},A{r},{R["statut"]},"Actif",{FV})')
    calc.cell(r, 3, f'=COUNTIFS({R["dept"]},A{r},{R["statut"]},"Parti",{FV})')
    calc.cell(r, 4, f"=IFERROR(C{r}/(B{r}+C{r}),0)")
    calc.cell(r, 5, f'=IFERROR(AVERAGEIFS({R["sal"]},{R["dept"]},A{r},{R["statut"]},"Actif",{FV}),0)')
    calc.cell(r, 6, f'=IFERROR(AVERAGEIFS({R["perf"]},{R["dept"]},A{r},{R["statut"]},"Actif",{FV}),0)')
    for c, fmt in zip(range(1, 7), [None, "#,##0", "#,##0", "0.0%", '#,##0 "€"', "0.00"]):
        body(calc, calc.cell(r, c), fmt)
d_end = 3 + len(depts)

# 2. Par poste
postes = ["Junior", "Confirmé", "Senior", "Manager"]
p0 = d_end + 3
header(calc, p0, 1, ["Poste", "Effectif actif", "Salaire moyen"])
for i, p in enumerate(postes):
    r = p0 + 1 + i
    calc.cell(r, 1, p)
    calc.cell(r, 2, f'=COUNTIFS({R["poste"]},A{r},{R["statut"]},"Actif",{FV})')
    calc.cell(r, 3, f'=IFERROR(AVERAGEIFS({R["sal"]},{R["poste"]},A{r},{R["statut"]},"Actif",{FV}),0)')
    for c, fmt in zip(range(1, 4), [None, "#,##0", '#,##0 "€"']):
        body(calc, calc.cell(r, c), fmt)
p_end = p0 + len(postes)

# 3. Embauches par année
years = list(range(2016, 2027))
y0 = p_end + 3
header(calc, y0, 1, ["Année", "Embauches"])
for i, y in enumerate(years):
    r = y0 + 1 + i
    calc.cell(r, 1, str(y))
    calc.cell(r, 2, f'=COUNTIFS({R["annee"]},{y},{FV})')
    body(calc, calc.cell(r, 1)); body(calc, calc.cell(r, 2), "#,##0")
y_end = y0 + len(years)

# 4. Turnover par niveau de satisfaction
s0 = y_end + 3
header(calc, s0, 1, ["Satisfaction", "Employés", "Départs", "Turnover"])
for i, s in enumerate(range(1, 6)):
    r = s0 + 1 + i
    calc.cell(r, 1, f"{s}/5")
    calc.cell(r, 2, f'=COUNTIFS({R["satis"]},{s},{FV})')
    calc.cell(r, 3, f'=COUNTIFS({R["satis"]},{s},{R["statut"]},"Parti",{FV})')
    calc.cell(r, 4, f"=IFERROR(C{r}/B{r},0)")
    for c, fmt in zip(range(1, 5), [None, "#,##0", "#,##0", "0.0%"]):
        body(calc, calc.cell(r, c), fmt)
s_end = s0 + 5

# ---------- Graphiques ----------
def style(ch, title, w=11.9, h=7.5):
    ch.title = title
    ch.width, ch.height = w, h
    ch.legend = None
    ch.style = 10
    return ch

ch1 = style(BarChart(), "Effectif actif par département")
ch1.type = "bar"
ch1.add_data(Reference(calc, min_col=2, min_row=3, max_row=d_end), titles_from_data=True)
ch1.set_categories(Reference(calc, min_col=1, min_row=4, max_row=d_end))
ch1.series[0].graphicalProperties.solidFill = GREEN
ch1.dataLabels = DataLabelList(showVal=True, showSerName=False, showCatName=False, showLegendKey=False, showPercent=False)
dash.add_chart(ch1, "B10")

ch2 = style(BarChart(), "Taux de turnover par département")
ch2.add_data(Reference(calc, min_col=4, min_row=3, max_row=d_end), titles_from_data=True)
ch2.set_categories(Reference(calc, min_col=1, min_row=4, max_row=d_end))
ch2.series[0].graphicalProperties.solidFill = "C0504D"
ch2.y_axis.numFmt = "0%"
ch2.dataLabels = DataLabelList(showVal=True, showSerName=False, showCatName=False, showLegendKey=False, showPercent=False, numFmt="0%")
dash.add_chart(ch2, "H10")

ch3 = style(PieChart(), "Répartition par poste", w=8.2)
ch3.add_data(Reference(calc, min_col=2, min_row=p0, max_row=p_end), titles_from_data=True)
ch3.set_categories(Reference(calc, min_col=1, min_row=p0 + 1, max_row=p_end))
ch3.dataLabels = DataLabelList(showPercent=True, showVal=False, showSerName=False, showCatName=False, showLegendKey=False)
from openpyxl.chart.legend import Legend
ch3.legend = Legend(); ch3.legend.position = "b"
dash.add_chart(ch3, "N10")

ch4 = style(LineChart(), "Embauches par année")
ch4.add_data(Reference(calc, min_col=2, min_row=y0, max_row=y_end), titles_from_data=True)
ch4.set_categories(Reference(calc, min_col=1, min_row=y0 + 1, max_row=y_end))
ch4.series[0].graphicalProperties.line.solidFill = GREEN
ch4.series[0].graphicalProperties.line.width = 28000
ch4.series[0].smooth = True
dash.add_chart(ch4, "B26")

ch5 = style(BarChart(), "Salaire moyen par département (€)")
ch5.add_data(Reference(calc, min_col=5, min_row=3, max_row=d_end), titles_from_data=True)
ch5.set_categories(Reference(calc, min_col=1, min_row=4, max_row=d_end))
ch5.series[0].graphicalProperties.solidFill = "4E9A6B"
ch5.y_axis.numFmt = "#,##0"
dash.add_chart(ch5, "H26")

ch6 = style(BarChart(), "Turnover selon la satisfaction", w=8.2)
ch6.add_data(Reference(calc, min_col=4, min_row=s0, max_row=s_end), titles_from_data=True)
ch6.set_categories(Reference(calc, min_col=1, min_row=s0 + 1, max_row=s_end))
ch6.series[0].graphicalProperties.solidFill = "E67E22"
ch6.y_axis.numFmt = "0%"
dash.add_chart(ch6, "N26")

# Axes visibles (openpyxl >= 3.1 les masque par défaut)
for ch in (ch1, ch2, ch4, ch5, ch6):
    ch.x_axis.delete = False
    ch.y_axis.delete = False

dash["B42"] = "Insight clé : le turnover chute fortement quand la satisfaction augmente — levier prioritaire pour la rétention."
dash["B42"].font = Font(name=F, italic=True, bold=True, color=GREEN)

wb.save("Dashboard_RH.xlsx")
print("ok")
