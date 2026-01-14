def score_entities(entities, metric_set):
    results = []

    for e in entities:
        total = 0.0
        confidence = 0.0

        for m in metric_set.metrics:
            signal = e["signals"].get(m.name, 0)
            total += signal * m.weight
            confidence += m.weight if signal > 0 else 0

        results.append({
            "name": e["name"],
            "url": e["url"],
            "score": round(total, 3),
            "confidence": round(confidence, 3)
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
