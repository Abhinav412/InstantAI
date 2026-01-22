from agents.orchestrator import run_agentic_chatbot as _core_chatbot


def run_dataset_chatbot(
    user_query: str,
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
    dataset_preview: list[dict],
):
    if not dataset_preview:
        return {
            "mode": "REFUSE",
            "reason": "No dataset context available for safe reasoning",
        }

    return _core_chatbot(
        user_query=user_query,
        knowledge_index=knowledge_index,
        allowed_metrics=allowed_metrics,
        blocked_metrics=blocked_metrics,
        low_trust_present=low_trust_present,
        dataset_preview=dataset_preview,
    )
