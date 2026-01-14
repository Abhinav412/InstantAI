from models.schema import MetricSet, MetricDefinition
from utils.llm import call_llm

def construct_metrics(intent, data_insights, external_data) -> MetricSet:
    system = "You define ranking metrics. Return ONLY valid JSON."
    user = f"""
    Intent: {intent}
    External records: {len(external_data.records)}

    Return JSON:
    {{
      "metrics": [
        {{ "name": str, "weight": float, "description": str }}
      ],
      "normalization": str
    }}

    Weights must sum to 1.
    """

    response = call_llm(system, user)

    # ✅ Normalize metric dicts → MetricDefinition objects
    metric_objects = [
        MetricDefinition(
            name=m["name"],
            weight=float(m["weight"]),
            description=m["description"]
        )
        for m in response["metrics"]
    ]

    return MetricSet(
        metrics=metric_objects,
        normalization=response["normalization"]
    )
