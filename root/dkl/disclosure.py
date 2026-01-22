def generate_disclosure(knowledge_index: dict) -> str:
    gaps = knowledge_index.get("data_gaps", [])

    if not gaps:
        return "All metrics are based on verified data sources."

    bullet_points = "\n".join(f"- {gap}" for gap in gaps)

    return (
        "⚠️ Data limitations apply:\n"
        f"{bullet_points}"
    )
