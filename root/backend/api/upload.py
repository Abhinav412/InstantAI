from fastapi import APIRouter, UploadFile, File
import pandas as pd

from backend.storage.dataset_store import save_dataset

router = APIRouter()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    elif file.filename.endswith(".json"):
        df = pd.read_json(file.file)
    else:
        return {"status": "ERROR", "reason": "Unsupported format"}

    dataset_id = save_dataset(df)

    return {
        "status": "OK",
        "dataset_id": dataset_id,
        "columns": list(df.columns),
        "rows": len(df),
    }
