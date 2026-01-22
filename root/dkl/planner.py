from dkl.gap_priority import compute_gap_priority

class DataGapPlanner:
    def __init__(self, gaps: list[dict]):
        self.gaps = gaps

    def plan(self) -> list[dict]:
        if not self.gaps:
            return []

        sorted_gaps = sorted(
            self.gaps,
            key=lambda g: compute_gap_priority(g),
            reverse=True,
        )

        return [
            {
                "action": gap["recommended_action"],
                "target_entity": gap["entity"],
                "metric": gap["metric"],
                "gap_id": gap["gap_id"],
            }
            for gap in sorted_gaps
        ]
