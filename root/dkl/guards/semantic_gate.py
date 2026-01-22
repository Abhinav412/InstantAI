def validate_metric_usage(metric: dict):
    if metric["usage_status"] != "ALLOWED":
        return {
            "allowed": False,
            "reason": "Metric is semantically ambiguous",
            "ambiguities": metric["ambiguity_flags"]
        }

    return {"allowed": True}
