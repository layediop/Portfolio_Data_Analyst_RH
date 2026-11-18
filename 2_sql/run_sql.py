"""Charge les données dans SQLite, exécute les requêtes et écrit les résultats en Markdown."""
import re
import sqlite3
import pandas as pd

con = sqlite3.connect("rh.db")
con.executescript(open("01_schema.sql", encoding="utf-8").read())
df = pd.read_csv("../data/employes.csv")
df.to_sql("employes", con, if_exists="append", index=False)

sql = open("02_analyses.sql", encoding="utf-8").read()
blocks = re.split(r"\n(?=-- Q\d+\.)", sql)
out = ["# Résultats des requêtes SQL\n", "_Exécutées sur SQLite — 1 000 employés fictifs._\n"]
for b in blocks:
    m = re.match(r"-- (Q\d+\..*)", b)
    if not m:
        continue
    query = b.strip()
    res = pd.read_sql_query(query, con)
    out.append(f"\n## {m.group(1)}\n")
    out.append("```sql\n" + query + "\n```\n")
    out.append(res.to_markdown(index=False) + "\n")
    print(m.group(1)); print(res.head(8).to_string(index=False)); print()
open("resultats.md", "w", encoding="utf-8").write("\n".join(out))
