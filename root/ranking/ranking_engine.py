import pandas as pd


class RankingEngine:
    def __init__(
        self,
        df: pd.DataFrame,
        kpi: str,
        entity_column: str,
    ):
        self.df = df
        self.kpi = kpi
        self.entity_column = entity_column

    def rank(self):
        if self.kpi not in self.df.columns:
            raise ValueError(f"KPI column '{self.kpi}' not found")

        if self.entity_column not in self.df.columns:
            raise ValueError(f"Entity column '{self.entity_column}' not found")

        working_df = (
            self.df[[self.entity_column, self.kpi]]
            .dropna()
            .sort_values(by=self.kpi, ascending=False)
            .reset_index(drop=True)
        )

        ranking = []
        for i, row in working_df.iterrows():
            ranking.append(
                {
                    "entity": row[self.entity_column],
                    "value": float(row[self.kpi]),
                    "rank": i + 1,
                }
            )

        return ranking
