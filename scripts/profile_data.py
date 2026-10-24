import pandas as pd

PATH = "data/DataCoSupplyChainDataset_nettoyees.csv"
df = pd.read_csv(PATH, encoding="latin-1")
df.columns = df.columns.str.strip()

print(df.shape)
print(df["Order Id"].nunique())
print(df["Shipping Mode"].value_counts())
print(df["Delivery Status"].value_counts(normalize=True))
print(df["Order Status"].value_counts())
print(df.groupby("Shipping Mode")["Days for shipment (scheduled)"].agg(["min", "max", "nunique"]))

# Cohérence : une même commande a-t-elle un seul mode / un seul statut de livraison ?
g = df.groupby("Order Id")[["Shipping Mode", "Delivery Status", "Days for shipping (real)"]].nunique()
print((g > 1).sum())

# Le statut « Late delivery » correspond-il à réel > prévu ?
late = df["Days for shipping (real)"] > df["Days for shipment (scheduled)"]
print(pd.crosstab(df["Delivery Status"], late))

# Dates, valeurs manquantes, encodage
dt = pd.to_datetime(df["order date (DateOrders)"], format="%m/%d/%Y %H:%M", errors="coerce")
print(dt.min(), dt.max(), dt.isna().sum())
print(df.isna().mean().sort_values(ascending=False).head(8))
print(df["Order City"].str.contains("Ã", na=False).sum())