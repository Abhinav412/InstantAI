from utils.llm import call_llm

MIN_DRIVERS = 3

def explain(rankings, metrics):
    system = """
    You are an explanation agent.

    RULES:
    - Return ONLY valid JSON
    - No code, no markdown, no backticks
    """

    user = f"""
    Rankings:
    {rankings}

    Metrics:
    {[{"name": m.name, "weight": m.weight} for m in metrics.metrics]}

    Return JSON:
    {{
      "summary": string,
      "top_drivers": [
        {{ "name": string, "reason": string }}
      ],
      "confidence_interpretation": string
    }}
    """

    response = call_llm(system, user)

    # ---------- CONTRACT ENFORCEMENT ----------
    drivers = response.get("top_drivers", [])

    # If LLM returned too few drivers, fill from metrics
    if len(drivers) < MIN_DRIVERS:
        existing = {d["name"] for d in drivers}

        for m in sorted(metrics.metrics, key=lambda x: x.weight, reverse=True):
            if m.name not in existing:
                drivers.append({
                    "name": m.name,
                    "reason": f"Metric '{m.name}' significantly influenced the final ranking."
                })
            if len(drivers) >= MIN_DRIVERS:
                break

    response["top_drivers"] = drivers[:MIN_DRIVERS]

    return response
