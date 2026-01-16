import numpy as np


def confidence(series):
    return float(round(series.notna().mean(), 2))
