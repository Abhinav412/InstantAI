from utils.llm import call_llm

def explain(rankings, metrics):
    system = """
    You are an explanation agent.

    RULES:
    - You MUST return ONLY a valid JSON object.
    - You MUST NOT return code.
    - You MUST NOT return markdown.
    - You MUST NOT return explanations outside JSON.
    - You MUST NOT use backticks.
    """

    user = f"""
    Rankings:
    {rankings}

    Metrics:
    {[{"name": m.name, "weight": m.weight} for m in metrics.metrics]}

    Return a JSON OBJECT with EXACT keys:
    {{
      "summary": string,
      "top_drivers": [
        {{ "name": string, "reason": string }}
      ],
      "confidence_interpretation": string
    }}

    If rankings are empty:
    - summary = "No rankings available"
    - top_drivers = []
    - confidence_interpretation = "Insufficient data"
    """

    response = call_llm(system, user)

    # ✅ Final hard guard
    if not isinstance(response, dict):
        raise ValueError(f"Explanation must be JSON object, got: {response}")

    return response
