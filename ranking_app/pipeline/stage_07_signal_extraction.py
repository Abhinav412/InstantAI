from utils.llm import call_llm

def extract_signals(entity, metrics):
    system = """
    You are a scoring agent.

    RULES:
    - You MUST assign a score between 0.1 and 1.0 for EVERY metric.
    - You MUST use the provided evidence text.
    - You MUST NOT return all zeros.
    - You MUST return ONLY valid JSON.
    """

    metric_names = [m.name for m in metrics.metrics]

    user = f"""
    Entity:
    Name: {entity["name"]}
    URL: {entity["url"]}

    Evidence:
    {entity["evidence"]}

    Metrics to score:
    {metric_names}

    Return a JSON OBJECT with EXACT structure:
    {{
      "signals": {{
        "<metric_name>": number between 0.1 and 1.0
      }}
    }}

    Scoring guidance:
    - If evidence STRONGLY supports metric → 0.7–1.0
    - If evidence WEAKLY supports metric → 0.4–0.6
    - If evidence is UNCLEAR → 0.1–0.3
    """

    response = call_llm(system, user)

    # Normalize
    if "signals" in response:
        return response["signals"]

    # Fallback: accept flat metric dict
    return {
        k: float(v)
        for k, v in response.items()
        if k in metric_names
    }
