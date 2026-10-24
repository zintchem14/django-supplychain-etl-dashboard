import numpy as np
import pandas as pd


def detect(rows, window=8, z_threshold=2.5, min_volume=30):
    # rows : [{"periode": date, "volume": int, "retards": int}, ...] (sortie de kpis.timeseries)
    if len(rows) < window // 2 + 2:
        return []
    df = pd.DataFrame(rows).sort_values("periode").reset_index(drop=True)
    df["taux"] = df["retards"] / df["volume"]
    prev = df["taux"].shift(1)
    df["base"] = prev.rolling(window, min_periods=window // 2).mean()
    sigma = prev.rolling(window, min_periods=window // 2).std()
    bruit = np.sqrt(df["base"] * (1 - df["base"]) / df["volume"])
    df["z"] = (df["taux"] - df["base"]) / np.maximum(sigma, bruit)
    hit = df[(df["z"] >= z_threshold) & (df["volume"] >= min_volume)]
    return [{"periode": r.periode, "taux": float(r.taux), "base": float(r.base),
             "z": float(r.z), "volume": int(r.volume)} for r in hit.itertuples()]