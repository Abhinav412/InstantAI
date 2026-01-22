from fastapi import APIRouter
from backend.storage.dataset_store import load_dataset_by_id
from pipeline.dataset_pipeline import process_user_dataset

router = APIRouter()


@router.post("/analyze")
def analyze_dataset(
    dataset_id: str,
    drop_columns: list[str] | None = None,
):
    df = load_dataset_by_id(dataset_id)

    return process_user_dataset(
        file_path=None,
        injected_df=df,
        drop_columns_list=drop_columns,
        dataset_origin="user",
    )
