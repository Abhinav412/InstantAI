from dkl.chatbot_modes import ChatbotMode


def decide_chat_action(
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
):
    """
    Central decision logic for:
    - answering
    - asking clarification
    - refusing

    This function is the ONLY place where this decision is made.
    """

    knowledge_state = knowledge_index.get("knowledge_state")
    data_gaps = knowledge_index.get("data_gaps", [])

    # ----------------------------------
    # 1. READY → full answer allowed
    # ----------------------------------
    if knowledge_state == "READY":
        return {
            "mode": ChatbotMode.FULL_ANSWER,
            "action": "SHOW_RANKING",
            "disclosure": (
                "Results are based on web-sourced data and may be incomplete."
                if low_trust_present
                else None
            ),
        }

    # ----------------------------------
    # 2. Knowledge incomplete → clarify
    # ----------------------------------
    if knowledge_state in {"PROFILED", "SEMANTIC_MAPPED"}:
        return {
            "mode": ChatbotMode.CLARIFICATION_ONLY,
            "action": "ASK_FOR_MORE_INFO",
            "missing_information": {
                "data_gaps": data_gaps,
                "blocked_metrics": blocked_metrics,
                "suggested_metrics": allowed_metrics,
            },
        }

    # ----------------------------------
    # 3. Anything else → refuse
    # ----------------------------------
    return {
        "mode": ChatbotMode.REFUSE,
        "reason": "Insufficient or unsafe data to answer this question",
    }
