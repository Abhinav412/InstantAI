from dkl.enums import TrustLevel


def compute_trust_weight(source: dict) -> float:
    """
    Converts trust metadata into a numeric weight (0.0 – 1.0)
    """

    base = {
        TrustLevel.HIGH.value: 1.0,
        TrustLevel.MEDIUM.value: 0.6,
        TrustLevel.LOW.value: 0.2,
    }[source["trust_level"]]

    score = base * source["confidence_score"]

    if not source["cross_verified"]:
        score *= 0.7

    if source.get("known_biases"):
        score *= 0.8

    return round(score, 3)
