def generate_explanation(programs, compiled):
    explanations = []

    used = {p.name for p, _ in compiled}

    for p in programs:
        if p.name not in used:
            continue

        explanations.append({
            "metric": p.name,
            "formula": p.expression,
            "direction": p.direction,
            "rationale": f"This metric was computed using available signals to represent '{p.name}' in the dataset."
        })

    return {
        "summary": "Rankings were computed using synthesized metric programs derived from the dataset.",
        "metrics_used": explanations
    }
