# data gap model
class DataGap:
    def __init__(
        self,
        gap_id: str,
        entity: str,
        metric: str,
        severity: str,
        impact: str,
        recommended_action: str,
    ):
        self.gap_id = gap_id
        self.entity = entity
        self.metric = metric
        self.severity = severity
        self.impact = impact
        self.recommended_action = recommended_action

    def to_dict(self) -> dict:
        return {
            "gap_id": self.gap_id,
            "entity": self.entity,
            "metric": self.metric,
            "severity": self.severity,
            "impact": self.impact,
            "recommended_action": self.recommended_action,
        }
