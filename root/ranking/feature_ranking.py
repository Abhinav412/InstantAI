import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression


def feature_importance(df: pd.DataFrame, target_col: str | None = None):
    """
    Computes feature importance using:
    - Mutual Information when sample size allows
    - Variance-based fallback when sample size is too small
    """

    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty:
        return {}

    if target_col and target_col in numeric_df.columns:
        y = numeric_df[target_col]
        X = numeric_df.drop(columns=[target_col])
    else:
        y = numeric_df.iloc[:, -1]
        X = numeric_df.iloc[:, :-1]

    if X.empty:
        return {}

    # 🚨 Safety: insufficient samples for MI
    if len(X) < 4:
        variances = X.var().sort_values(ascending=False)
        return variances.to_dict()

    # Safe MI computation
    n_neighbors = min(3, len(X) - 1)

    scores = mutual_info_regression(
        X,
        y,
        n_neighbors=n_neighbors,
        random_state=42,
    )

    return dict(zip(X.columns, scores))


def analyze_clusters_with_kpi(
    df: pd.DataFrame,
    kpi: str,
    cluster_col: str,
    top_n_features: int = 5,
):
    results = {}

    cluster_stats = (
        df.groupby(cluster_col)[kpi]
        .agg(["mean", "median", "count"])
        .reset_index()
    )

    best_cluster = cluster_stats.sort_values("mean", ascending=False).iloc[0]
    worst_cluster = cluster_stats.sort_values("mean").iloc[0]

    best_id = best_cluster[cluster_col]
    worst_id = worst_cluster[cluster_col]

    results["kpi_stats"] = cluster_stats.to_dict(orient="records")

    results["global_drivers"] = feature_importance(df, kpi)

    results["good_cluster_drivers"] = feature_importance(
        df[df[cluster_col] == best_id], kpi
    )

    results["bad_cluster_drivers"] = feature_importance(
        df[df[cluster_col] == worst_id], kpi
    )

    results["comparison"] = {
        "best_cluster_id": int(best_id),
        "worst_cluster_id": int(worst_id),
        "best_cluster_mean": float(best_cluster["mean"]),
        "worst_cluster_mean": float(worst_cluster["mean"]),
    }

    return normalize(results)


def normalize(obj):
    """
    Recursively converts NumPy / Pandas scalar types
    into native Python types for safe JSON / API usage.
    """
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [normalize(v) for v in obj]

    if hasattr(obj, "item"):
        return obj.item()

    return obj
