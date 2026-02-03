from agents.chat_decision import decide_chat_action
from agents.reasoning_agent import reason
from agents.chatbot.clarification import build_clarification_response
from agents.chatbot.system_context import build_system_context


def run_chat_runtime(
    user_query: str,
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
    dataset_preview: list[dict] | None = None,
):
    decision = decide_chat_action(
        knowledge_index=knowledge_index,
        allowed_metrics=allowed_metrics,
        blocked_metrics=blocked_metrics,
        low_trust_present=low_trust_present,
    )

    if "market_cap" in allowed_metrics:
        if not any("market_cap" in row for row in dataset_preview):
            return {
                "mode": "CLARIFICATION_ONLY",
                "response": (
                    "I understand the ranking metric, but market capitalization "
                    "values are missing. Should I fetch them from the web?"
                ),
            }

    # -----------------------------------------
    # 1. CLARIFICATION
    # -----------------------------------------
    if decision["mode"] == "CLARIFICATION_ONLY":
        return {
            "mode": "CLARIFICATION_ONLY",
            "response": build_clarification_response(
                allowed_metrics=allowed_metrics,
                blocked_metrics=blocked_metrics,
            ),
            "details": decision.get("missing_information"),
        }

    # -----------------------------------------
    # 2. REFUSAL
    # -----------------------------------------
    if decision["mode"] == "REFUSE":
        return {
            "mode": "REFUSE",
            "response": decision.get("reason"),
        }

    # -----------------------------------------
    # 3. FULL ANSWER (LLM REASONING)
    # -----------------------------------------
    system_context = build_system_context(
        knowledge_index=knowledge_index,
        allowed_metrics=allowed_metrics,
        low_trust_present=low_trust_present,
        dataset_preview=dataset_preview,
    )

    llm_response = reason(
        prompt=user_query,
        system_context=system_context,
    )

    return {
        "mode": "FULL_ANSWER",
        "response": llm_response,
    }
