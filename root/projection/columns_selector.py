import pandas as pd


def drop_columns(
    df: pd.DataFrame,
    drop_columns: list[str],
    required_columns: list[str] | None = None,
) -> pd.DataFrame:
    working_df = df.copy()

    required_columns = required_columns or []

    for col in drop_columns:
        if col in required_columns:
            continue
        if col in working_df.columns:
            working_df = working_df.drop(columns=[col])

    return working_df
