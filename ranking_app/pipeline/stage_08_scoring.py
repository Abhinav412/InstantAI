def score_entities(entities, metric_set):
    results = []

    for e in entities:
        weighted_score = 0.0
        weighted_confidence = 0.0
        weight_sum = 0.0

        for m in metric_set.metrics:
            signal = float(e["signals"].get(m.name, 0.0))

            weighted_score += signal * m.weight
            weighted_confidence += signal * m.weight
            weight_sum += m.weight

        # Normalize confidence to [0, 1]
        confidence = (
            weighted_confidence / weight_sum
            if weight_sum > 0
            else 0.0
        )

        results.append({
            "name": e["name"],
            "url": e["url"],
            "score": round(weighted_score, 3),
            "confidence": round(min(confidence, 1.0), 2)
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
