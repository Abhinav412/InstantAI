import pandas as pd

from dkl.models.data_profile import DataProfile


class DataProfiler:
    def profile(self, dataset_id: str, df: pd.DataFrame) -> DataProfile:
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }

        return DataProfile(
            dataset_id=dataset_id,
            stats=stats
        )
