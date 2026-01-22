import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def cluster_from_ranking(ranking: list[dict], n_clusters: int = 3):
    if not ranking:
        return []

    values = np.array([r["value"] for r in ranking]).reshape(-1, 1)

    if len(values) < n_clusters:
        n_clusters = max(1, len(values))

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(values)

    clustered = []
    for item, label in zip(ranking, labels):
        enriched = dict(item)
        enriched["cluster_id"] = int(label)
        clustered.append(enriched)

    return clustered
