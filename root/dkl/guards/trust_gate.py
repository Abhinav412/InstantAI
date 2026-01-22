def enforce_trust_gate(source: dict, min_weight: float = 0.5):
    from dkl.trust_engine import compute_trust_weight

    weight = compute_trust_weight(source)

    if weight < min_weight:
        return {
            "allowed": False,
            "reason": "Source trust too low",
            "trust_weight": weight,
        }

    return {
        "allowed": True,
        "trust_weight": weight,
    }
