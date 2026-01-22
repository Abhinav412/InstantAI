class SemanticRegistry:
    def __init__(self):
        self.metrics: dict[str, dict] = {}

    def register(self, metric):
        if metric.metric_id in self.metrics:
            raise ValueError(f"Metric {metric.metric_id} already registered")

        self.metrics[metric.metric_id] = metric.to_dict()

    def get_allowed_metrics(self):
        return {
            k: v for k, v in self.metrics.items()
            if v["usage_status"] == "ALLOWED"
        }

    def get_blocked_metrics(self):
        return {
            k: v for k, v in self.metrics.items()
            if v["usage_status"] == "BLOCKED"
        }
