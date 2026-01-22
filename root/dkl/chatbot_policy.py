from dkl.chatbot_modes import ChatbotMode


def decide_chatbot_mode(
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
):
    # 1. Knowledge not ready → hard block
    if knowledge_index.get("knowledge_state") != "READY":
        return ChatbotMode.CLARIFICATION_ONLY, "Data knowledge incomplete"

    # 2. No valid metrics → cannot rank or reason
    if not allowed_metrics:
        return ChatbotMode.CLARIFICATION_ONLY, "No semantically valid metrics available"

    # 3. Low trust data involved → disclosure required
    if low_trust_present:
        return ChatbotMode.DISCLOSURE_ONLY, "Low trust data involved"

    # 4. All checks passed → full answer allowed
    return ChatbotMode.FULL_ANSWER, None
