import pandas as pd
from dataclasses import dataclass


@dataclass
class DatasetAudit:
    df: pd.DataFrame
    columns: list
    numeric_columns: list
    categorical_columns: list
    row_count: int


def audit_dataset(input_data):
    # ---- CASE 1: DataFrame passed directly ----
    if isinstance(input_data, pd.DataFrame):
        df = input_data.copy()

    # ---- CASE 2: File path passed ----
    elif isinstance(input_data, str):
        try:
            df = pd.read_csv(input_data, encoding="utf-8")
        except Exception:
            df = pd.read_csv(input_data, encoding="latin1")

    else:
        raise TypeError(
            "audit_dataset expects a pandas DataFrame or a file path"
        )

    if df.empty:
        raise ValueError("Dataset is empty")

    df.columns = [c.strip() for c in df.columns]

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = [
        c for c in df.columns if c not in numeric_columns
    ]

    return DatasetAudit(
        df=df,
        columns=df.columns.tolist(),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        row_count=len(df)
    )
