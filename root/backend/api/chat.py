from fastapi import APIRouter, Query
import pandas as pd

from backend.storage.dataset_store import get_dataset
from pipeline.dataset_pipeline import process_user_dataset
from agents.chat_runtime import run_dataset_chatbot

router = APIRouter()


@router.post("/chat")
def chat_with_dataset(
    dataset_id: str = Query(...),
    user_query: str = Query(...),
    drop_columns: list[str] | None = Query(default=None),
):
    df: pd.DataFrame = get_dataset(dataset_id)

    system_state = process_user_dataset(
        file_path=None,
        injected_df=df,
        drop_columns_list=drop_columns or [],
        dataset_origin="user",
    )

    dataset_preview = df.head(5).to_dict(orient="records")

    return run_dataset_chatbot(
        user_query=user_query,
        knowledge_index=system_state["knowledge_index"],
        allowed_metrics=system_state["allowed_metrics"],
        blocked_metrics=system_state["blocked_metrics"],
        low_trust_present=system_state["low_trust_present"],
        dataset_preview=dataset_preview,
    )
