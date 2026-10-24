import pandas as pd

SOURCE = "data/DataCoSupplyChainDataset.csv"
CIBLE = "data/samples/mini.csv"

# 30 premières lignes, lues sans conversion pour garder le format d'origine
df = pd.read_csv(SOURCE, nrows=30, dtype=str, keep_default_na=False, encoding="latin-1")

# 3 lignes volontairement invalides, sur de nouvelles commandes
bad = df.tail(3).copy()
bad["Order Id"] = ["999001", "999002", "999003"]
bad.iloc[0, bad.columns.get_loc("Days for shipping (real)")] = "-1"   # délai réel négatif
bad.iloc[1, bad.columns.get_loc("Shipping Mode")] = "Drone"          # mode d'expédition inconnu
bad.iloc[2, bad.columns.get_loc("order date (DateOrders)")] = ""     # date de commande vide

pd.concat([df, bad]).to_csv(CIBLE, index=False, encoding="latin-1")
print(f"{CIBLE} : {len(df)} lignes valides + {len(bad)} lignes invalides")