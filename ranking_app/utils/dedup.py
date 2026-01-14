def deduplicate_rankings(rankings, strategy="max"):
    """
    Deduplicate ranked entities by name.

    strategy:
    - "max": keep highest score
    - "avg": average scores
    """

    by_name = {}

    for r in rankings:
        name = r["name"].strip().lower()

        if name not in by_name:
            by_name[name] = {
                "name": r["name"],
                "url": r["url"],
                "score": r["score"],
                "confidence": r["confidence"],
                "count": 1
            }
        else:
            if strategy == "max":
                if r["score"] > by_name[name]["score"]:
                    by_name[name]["score"] = r["score"]
                    by_name[name]["url"] = r["url"]

            elif strategy == "avg":
                by_name[name]["score"] += r["score"]
                by_name[name]["confidence"] += r["confidence"]
                by_name[name]["count"] += 1

    if strategy == "avg":
        for v in by_name.values():
            v["score"] /= v["count"]
            v["confidence"] /= v["count"]
            del v["count"]
    else:
        for v in by_name.values():
            del v["count"]

    return sorted(by_name.values(), key=lambda x: x["score"], reverse=True)
