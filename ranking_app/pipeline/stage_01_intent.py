from utils.llm import call_llm
from models.schema import TaskIntent


def infer_intent(query: str) -> TaskIntent:
    system = """
    You are an intent inference agent.

    STRICT RULES:
    - Return ONLY a single valid JSON object
    - Do NOT include explanations
    - Do NOT include markdown
    - Do NOT include comments
    - Do NOT include multiple JSON blocks
    - Do NOT revise your answer
    - Output MUST start with { and end with }

    If you violate this, the output will be discarded.
    """

    user = f"""
    Query: "{query}"

    Return EXACTLY this JSON structure:

    {{
      "task_type": string,
      "entity_type": string,
      "scope": string,
      "top_k": integer,
      "ranking_nature": string,
      "user_constraints": object
    }}

    Rules:
    - top_k MUST be an integer
    - If top_k is not specified, infer a reasonable default (e.g., 10)
    - user_constraints MUST be an object (use {{}} if none)
    """

    response = call_llm(system, user)

    # ---- HARD GUARANTEES (no structure change) ----
    if not isinstance(response, dict):
        raise TypeError(f"Intent must be object, got {type(response)}")

    # Defensive coercion (critical)
    if "top_k" in response:
        response["top_k"] = int(response["top_k"])

    return TaskIntent(**response)
