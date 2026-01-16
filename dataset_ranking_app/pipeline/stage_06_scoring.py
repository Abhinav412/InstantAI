import pandas as pd
import numpy as np
import pandas as pd


def sanitize_scores(df: pd.DataFrame):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)
    return df



def score_entities(valid_programs):
    scores = None
    breakdown = {}

    total_weight = sum(p.weight for p, _ in valid_programs)

    for program, series in valid_programs:
        norm = (series - series.min()) / (series.max() - series.min() + 1e-9)
        weighted = norm * (program.weight / total_weight)

        breakdown[program.name] = weighted
        scores = weighted if scores is None else scores + weighted

    return scores, breakdown
