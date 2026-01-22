from dkl.chatbot_guard import enforce_chatbot_guard
from agents.reasoning_agent import reason


def run_agentic_chatbot(
    user_query: str,
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
    dataset_preview: dict | None = None,
):
    guard = enforce_chatbot_guard(
        knowledge_index=knowledge_index,
        allowed_metrics=allowed_metrics,
        blocked_metrics=blocked_metrics,
        low_trust_present=low_trust_present,
    )

    mode = guard["mode"]

    # 🚫 Absolute safety rule
    if not dataset_preview:
        return {
            "mode": "REFUSE",
            "reason": "No dataset context available for safe reasoning",
        }

    dataset_context = f"""
DATASET FACTS (ONLY SOURCE OF TRUTH):

Sample rows:
{dataset_preview}

Allowed metrics:
{allowed_metrics}

Blocked metrics:
{blocked_metrics}
"""

    # 1️⃣ CLARIFICATION ONLY
    if mode == "CLARIFICATION_ONLY":
        return {
            "mode": mode,
            "response": (
                "I cannot answer yet because the dataset is incomplete or unclear. "
                "Please resolve the missing or ambiguous information."
            ),
            "details": guard,
        }

    # 2️⃣ DISCLOSURE ONLY (DATASET-BOUND)
    if mode == "DISCLOSURE_ONLY":
        system_context = f"""
You are a cautious analytical assistant.

STRICT RULES:
- Use ONLY the dataset facts provided
- DO NOT mention any real-world companies not in the dataset
- DO NOT use external knowledge
- DO NOT invent examples
- If the dataset is insufficient, say so clearly

{dataset_context}
"""

        response = reason(user_query, system_context)

        return {
            "mode": mode,
            "response": response,
            "disclosure": guard.get("disclosure"),
        }

    # 3️⃣ FULL ANSWER (STILL DATASET-BOUND)
    system_context = f"""
You are an expert analytical assistant.

STRICT RULES:
- Answer ONLY using the dataset facts provided
- Rank or compare ONLY entities present in the dataset
- DO NOT use any external knowledge
- DO NOT invent companies, numbers, or facts
- Explain uncertainty explicitly if trust is low

{dataset_context}
"""

    response = reason(user_query, system_context)

    return {
        "mode": mode,
        "response": response,
        "disclosure": guard.get("disclosure"),
    }


# ======================================================================
# ✅ APPENDED ONLY — DYNAMIC DATASET SUPPORT (NO MODIFICATIONS ABOVE)
# ======================================================================

def run_agentic_chatbot_with_dataset(
    user_query: str,
    knowledge_index: dict,
    allowed_metrics: list[str],
    blocked_metrics: list[str],
    low_trust_present: bool,
    dataframe,
    preview_rows: int = 5,
):
    """
    Wrapper that makes the chatbot work with ANY dataset dynamically.
    Original dataset remains intact; only a preview is passed.
    """

    if dataframe is None:
        return {
            "mode": "REFUSE",
            "reason": "No dataset provided for safe reasoning",
        }

    try:
        dataset_preview = dataframe.head(preview_rows).to_dict(orient="records")
    except Exception as e:
        return {
            "mode": "REFUSE",
            "reason": f"Failed to create dataset preview: {str(e)}",
        }

    return run_agentic_chatbot(
        user_query=user_query,
        knowledge_index=knowledge_index,
        allowed_metrics=allowed_metrics,
        blocked_metrics=blocked_metrics,
        low_trust_present=low_trust_present,
        dataset_preview=dataset_preview,
    )
