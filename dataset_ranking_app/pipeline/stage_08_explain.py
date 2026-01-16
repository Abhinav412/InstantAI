def explain(programs):
    return {
        "summary": "Ranking computed using dataset-derived metrics.",
        "metrics": [p.name for p in programs]
    }
