from dkl.chatbot_policy import decide_chatbot_mode
from dkl.disclosure import generate_disclosure
from dkl.chatbot_modes import ChatbotMode


def enforce_chatbot_guard(
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
):
    mode, reason = decide_chatbot_mode(
        knowledge_index,
        allowed_metrics,
        blocked_metrics,
        low_trust_present,
    )

    response = {"mode": mode.value}

    if reason:
        response["reason"] = reason

    if mode in {ChatbotMode.DISCLOSURE_ONLY, ChatbotMode.FULL_ANSWER}:
        response["disclosure"] = generate_disclosure(knowledge_index)

    return response
