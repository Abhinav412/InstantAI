import pandas as pd


def min_max_normalize(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (x - min_val) / (max_val - min_val)

    return normalized
