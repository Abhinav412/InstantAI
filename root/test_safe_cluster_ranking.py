import pandas as pd
from ranking.run_ranking import run_safe_cluster_ranking


def test_safe_cluster_ranking():
    df = pd.DataFrame({
        "hierarchical_cluster": [0, 0, 1, 1, 2, 2],
        "annual_revenue_usd": [10, 12, 5, 4, 20, 22],
        "funding_usd": [100, 120, 80, 75, 200, 210],
        "employees": [10, 12, 8, 9, 20, 22],
    })

    metric = {
        "metric_id": "annual_revenue_usd",
        "source_field": "annual_revenue_usd",
        "higher_is_better": True,
        "usage_status": "ALLOWED",
    }

    source = {
        "trust_level": "HIGH",
        "confidence_score": 0.95,
        "cross_verified": True,
        "known_biases": [],
    }

    result = run_safe_cluster_ranking(
        df=df,
        metric=metric,
        source=source,
        cluster_col="hierarchical_cluster",
        knowledge_index={"knowledge_state": "READY"},
        allowed_metrics=["annual_revenue_usd"],
    )

    print(result)


if __name__ == "__main__":
    test_safe_cluster_ranking()
