SEVERITY_SCORE = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}

IMPACT_SCORE = {
    "minor": 1,
    "ranking_quality": 2,
    "blocking": 3,
}

def compute_gap_priority(gap: dict) -> int:
    return (
        SEVERITY_SCORE.get(gap["severity"], 0)
        + IMPACT_SCORE.get(gap["impact"], 0)
    )
