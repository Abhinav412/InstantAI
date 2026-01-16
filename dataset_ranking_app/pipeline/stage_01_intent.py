from dataclasses import dataclass
from utils.llm import call_llm

@dataclass
class RankingIntent:
    entity_column: str
    metrics: dict


def infer_intent(query: str) -> RankingIntent:
    system = """
    You extract ranking intent from user queries.
    Return ONLY valid JSON.
    """

    user = f"""
    Query: {query}

    Return JSON:
    {{
      "entity_column": string,
      "metrics": {{ metric_name: weight }}
    }}
    """

    result = call_llm(system, user)

    if "entity_column" not in result or "metrics" not in result:
        raise ValueError("Invalid intent format from LLM")

    return RankingIntent(
        entity_column=result["entity_column"],
        metrics=result["metrics"]
    )
