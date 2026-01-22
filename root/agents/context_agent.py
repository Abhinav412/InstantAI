import json
from agents.reasoning_agent import reason


def infer_dataset_context(sample_rows: dict) -> dict:
    system_context = """
You are a data understanding agent.
You must output STRICT JSON.
Do NOT invent fields.
If unsure, return empty objects.
"""

    prompt = f"""
Dataset sample:
{sample_rows}

Infer:
- primary_entity
- candidate_metrics (column_name -> meaning)
- ambiguity_flags (column_name -> list)
"""

    response = reason(prompt, system_context)

    try:
        parsed = json.loads(response)
        if not isinstance(parsed, dict):
            return {}
        return parsed
    except Exception:
        return {}
