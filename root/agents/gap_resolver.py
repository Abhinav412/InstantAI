from dkl.planner import DataGapPlanner
from dkl.guards.planner_gate import enforce_planner_gate
from dkl.trust_engine import compute_trust_weight
from agents.free_retriever import fetch_public_sources


def resolve_data_gaps(data_gaps: list[dict]) -> list[dict]:
    """
    Resolves ONLY planner-approved gaps using free, public sources.
    """

    gate = enforce_planner_gate(data_gaps)
    if not gate["allowed"]:
        return []

    planner = DataGapPlanner(data_gaps)
    tasks = planner.plan()

    resolved = []

    for task in tasks:
        if task["action"] != "crawl_secondary_sources":
            continue

        results = fetch_public_sources(
            entity=task["target_entity"],
            metric=task["metric"],
        )

        for item in results:
            # 🔒 Always LOW TRUST by default
            source_metadata = {
                "source_id": item.get("url") or "wikipedia",
                "trust_level": "LOW",
                "confidence_score": 0.4,
                "cross_verified": False,
                "known_biases": ["open_encyclopedia"],
            }

            trust_weight = compute_trust_weight(source_metadata)

            resolved.append({
                "gap_id": task["gap_id"],
                "entity": task["target_entity"],
                "metric": task["metric"],
                "source": item.get("source"),
                "url": item.get("url"),
                "snippet": item.get("snippet"),
                "trust_weight": trust_weight,
            })

    return resolved
