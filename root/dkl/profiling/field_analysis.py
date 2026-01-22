import pandas as pd

def analyze_field(series: pd.Series) -> dict:
    total = len(series)
    missing = series.isna().sum()
    return {
        "missing_ratio": missing / total if total else 0,
        "unique_ratio": series.nunique(dropna=True) / total if total else 0
    }
