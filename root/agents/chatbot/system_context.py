def build_system_context(
    knowledge_index: dict,
    allowed_metrics: list[str],
    low_trust_present: bool,
    dataset_preview: list[dict] | None,
) -> str:
    lines = []

    lines.append("You are an analytical ranking assistant.")
    lines.append(
        f"Knowledge state: {knowledge_index.get('knowledge_state')}"
    )

    if allowed_metrics:
        lines.append(
            "Allowed ranking metrics: "
            + ", ".join(allowed_metrics)
        )

    if low_trust_present:
        lines.append(
            "WARNING: Data is web-sourced and may be incomplete."
        )

    if dataset_preview:
        lines.append("Sample data:")
        for row in dataset_preview[:5]:
            lines.append(str(row))

    lines.append(
        "Do not assume missing data. "
        "If something is unclear, say so explicitly."
    )

    return "\n".join(lines)
