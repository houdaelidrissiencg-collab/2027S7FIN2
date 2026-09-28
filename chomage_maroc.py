"""
Chômage au Maroc : importation des données et génération d'un graphique.

Sources des données :
 - HCP (Haut-Commissariat au Plan) : fichier local donnees_hcp.csv (séries annuelles,
   chaque ligne référence sa source, voir le rapport).
 - Banque mondiale (API, estimation modélisée OIT) : indicateur SL.UEM.TOTL.ZS
   (comparaison uniquement ; ajoutée au graphique si l'API répond).

Usage : pip install pandas matplotlib requests
        python chomage_maroc.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1) Import Banque mondiale (chômage total, % de la population active, Maroc)
URL_WB = ("https://api.worldbank.org/v2/country/MAR/indicator/"
          "SL.UEM.TOTL.ZS?format=json&per_page=100&date=2019:2025")
try:
    rep = requests.get(URL_WB, timeout=20).json()[1]
    wb = (pd.DataFrame(rep)[["date", "value"]]
          .rename(columns={"date": "annee", "value": "wb"})
          .astype({"annee": int}).dropna().sort_values("annee"))
except Exception as e:
    print("API Banque mondiale indisponible :", e)
    wb = pd.DataFrame(columns=["annee", "wb"])

# 2) Import HCP (fichier CSV)
hcp = pd.read_csv("donnees_hcp.csv")

# 3) Indicateurs
hcp["variation_pts"] = hcp["taux_chomage_national"].diff()
print(hcp[["annee", "taux_chomage_national", "variation_pts"]].to_string(index=False))
n19 = hcp.loc[hcp.annee == 2019, "taux_chomage_national"].iloc[0]
n23 = hcp.loc[hcp.annee == 2023, "taux_chomage_national"].iloc[0]
j20 = hcp.loc[hcp.annee == 2020, "jeunes_15_24"].iloc[0]
j25 = hcp.loc[hcp.annee == 2025, "jeunes_15_24"].iloc[0]
print(f"\nNational 2019 -> 2023 : {n23 - n19:+.1f} points")
print(f"Jeunes 15-24 ans 2020 -> 2025 : {j25 - j20:+.1f} points")

# 4) Graphique (2 panneaux)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
a1.plot(hcp.annee, hcp.taux_chomage_national, "o-", lw=2.5, color="#c0392b", label="National")
a1.plot(hcp.annee, hcp.taux_urbain, "s--", color="#2c3e50", label="Urbain")
a1.plot(hcp.annee, hcp.taux_rural, "^--", color="#27ae60", label="Rural")
if not wb.empty:
    a1.plot(wb.annee, wb.wb, ":", color="grey", label="Estimation OIT (Banque mondiale)")
for x, y in zip(hcp.annee, hcp.taux_chomage_national):
    a1.annotate(f"{y}", (x, y), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
a1.set_title("Chômage : national, urbain, rural (%)")

for col, lab, c in [("jeunes_15_24", "Jeunes 15-24 ans", "#8e44ad"),
                    ("diplomes", "Diplômés", "#e67e22"),
                    ("femmes", "Femmes", "#16a085")]:
    d = hcp.dropna(subset=[col])
    a2.plot(d.annee, d[col], "o-", label=lab, color=c)
a2.set_title("Chômage par catégorie (%)")

for a in (a1, a2):
    a.set_xlabel("Année"); a.set_ylabel("% de la population active")
    a.grid(alpha=.3); a.legend(fontsize=8)
fig.suptitle("Taux de chômage au Maroc, 2019-2025 (source : HCP)", fontweight="bold")
plt.tight_layout()
plt.savefig("graphique_chomage_maroc.png", dpi=150)
print("Graphique enregistré : graphique_chomage_maroc.png")
