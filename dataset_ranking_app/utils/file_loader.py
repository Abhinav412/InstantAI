import pandas as pd


def load_dataframe(path: str) -> pd.DataFrame:
    encodings = ["utf-8", "latin1", "cp1252"]

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "Unable to read file. Please upload a valid CSV (UTF-8 or Excel-exported)."
    )
