import pandas as pd


def rank_entities(df, entity_column, metric_map):
    if entity_column not in df.columns:
        raise ValueError(f"Entity column '{entity_column}' not found")

    total_weight = sum(metric_map.values())
    if total_weight == 0:
        raise ValueError("Metric weights sum to zero")

    working = df[[entity_column] + list(metric_map.keys())].copy()

    for metric in metric_map:
        col = working[metric].astype(float)
        min_v, max_v = col.min(), col.max()
        working[metric] = (col - min_v) / (max_v - min_v + 1e-9)

    working["score"] = 0.0
    for metric, weight in metric_map.items():
        working["score"] += working[metric] * (weight / total_weight)

    ranked = (
        working
        .groupby(entity_column, as_index=False)
        .mean(numeric_only=True)
        .sort_values("score", ascending=False)
    )

    return ranked
