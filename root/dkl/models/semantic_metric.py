# semantic metric model
from dkl.enums import ProfileStatus

class SemanticMetric:
    def __init__(
        self,
        metric_id: str,
        source_field: str,
        entity: str,
        definition: str,
        semantic_type: str,
        unit: str,
        time_scope: str,
        higher_is_better: bool,
        comparable_across_entities: bool,
        normalization: str | None = None,
        ambiguity_flags: list[str] | None = None,
    ):
        self.metric_id = metric_id
        self.source_field = source_field
        self.entity = entity
        self.definition = definition
        self.semantic_type = semantic_type
        self.unit = unit
        self.time_scope = time_scope
        self.higher_is_better = higher_is_better
        self.comparable_across_entities = comparable_across_entities
        self.normalization = normalization
        self.ambiguity_flags = ambiguity_flags or []

        self.usage_status = (
            "BLOCKED" if self.ambiguity_flags else "ALLOWED"
        )

    def to_dict(self) -> dict:
        return {
            "metric_id": self.metric_id,
            "source_field": self.source_field,
            "entity": self.entity,
            "definition": self.definition,
            "semantic_type": self.semantic_type,
            "unit": self.unit,
            "time_scope": self.time_scope,
            "higher_is_better": self.higher_is_better,
            "comparable_across_entities": self.comparable_across_entities,
            "normalization": self.normalization,
            "ambiguity_flags": self.ambiguity_flags,
            "usage_status": self.usage_status,
        }
