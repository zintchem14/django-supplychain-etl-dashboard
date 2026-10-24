import pandas as pd

from .config import COLUMNS, ENCODING


def extract(path, limit=None) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        encoding=ENCODING,
        usecols=lambda c: c.strip() in COLUMNS,
        nrows=limit,
    )
    df.columns = df.columns.str.strip()
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes absentes du fichier source : {sorted(missing)}")
    return df.rename(columns=COLUMNS)