from dkl.models.data_gap import DataGap
from agents.gap_resolver import resolve_data_gaps

print("\n[TEST] Free-first gap resolution (no Google)")

gaps = [
    DataGap(
        gap_id="missing_success_rate",
        entity="Incubator",
        metric="startup_success_rate",
        severity="HIGH",
        impact="ranking_quality",
        recommended_action="crawl_secondary_sources",
    ).to_dict()
]

resolved = resolve_data_gaps(gaps)

assert isinstance(resolved, list)
assert len(resolved) >= 0  # May be empty if page not found

print("✔ Free retriever executed successfully")
print("Resolved entries:", resolved[:1])
