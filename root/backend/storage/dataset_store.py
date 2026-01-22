import pandas as pd
from pymongo import MongoClient
import uuid
import os


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "agentic_analytics")
COLLECTION = "datasets"

_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]
_collection = _db[COLLECTION]


def save_dataset(df: pd.DataFrame) -> str:
    dataset_id = str(uuid.uuid4())

    document = {
        "_id": dataset_id,
        "columns": list(df.columns),
        "rows": df.to_dict(orient="records"),
        "row_count": len(df),
    }

    _collection.insert_one(document)
    return dataset_id


def get_dataset(dataset_id: str) -> pd.DataFrame:
    doc = _collection.find_one({"_id": dataset_id})

    if not doc:
        raise KeyError("Dataset not found")

    return pd.DataFrame(doc["rows"])


def delete_dataset(dataset_id: str):
    _collection.delete_one({"_id": dataset_id})

def load_dataset_by_id(dataset_id: str) -> pd.DataFrame:
    return get_dataset(dataset_id)
