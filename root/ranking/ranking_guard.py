def can_rank(
    knowledge_index: dict,
    allowed_metrics: list[str],
):
    if knowledge_index["knowledge_state"] != "READY":
        return False, "Knowledge layer not READY"

    if not allowed_metrics:
        return False, "No allowed semantic metrics available"

    return True, None
