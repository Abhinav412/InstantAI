import pandas as pd
from pipeline.dataset_pipeline import process_user_dataset
from agents.orchestrator import run_agentic_chatbot


def chat_with_dataset(
    user_query: str,
    dataset_path: str,
    drop_columns: list[str] | None = None,
):
    system_state = process_user_dataset(
        file_path=dataset_path,
        drop_columns=drop_columns,
        required_columns=[],  # enforced later at ranking time
    )

    if system_state.get("status") == "BLOCKED":
        return {
            "mode": "CLARIFICATION_ONLY",
            "reason": system_state["reason"],
        }

    dataset_preview = system_state["working_df"].head(5).to_dict()

    return run_agentic_chatbot(
        user_query=user_query,
        knowledge_index=system_state["knowledge_index"],
        allowed_metrics=system_state["allowed_metrics"],
        blocked_metrics=system_state["blocked_metrics"],
        low_trust_present=system_state["low_trust_present"],
        dataset_preview=dataset_preview,
    )
