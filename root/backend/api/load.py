from fastapi import APIRouter
from backend.storage.dataset_store import get_dataset

router = APIRouter()


@router.get("/dataset/{dataset_id}")
def load_dataset(dataset_id: str):
    try:
        df = get_dataset(dataset_id)
        
        return {
            "status": "OK",
            "dataset_id": dataset_id,
            "profile": {
                "fields": {
                    "column_count": len(df.columns),
                    "row_count": len(df),
                    "columns": list(df.columns)
                }
            },
            "data": df.head(10).to_dict(orient="records")
        }
    except KeyError:
        return {
            "status": "ERROR",
            "reason": "Dataset not found",
            "dataset_id": dataset_id
        }
