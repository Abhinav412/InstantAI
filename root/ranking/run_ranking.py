from ranking.ranking_engine import RankingEngine
from ranking.cluster_engine import cluster_from_ranking


def run_safe_kpi_ranking(
    df,
    kpi: str,
    entity_column: str,
    clustering: str = "none",
):
    engine = RankingEngine(
        df=df,
        kpi=kpi,
        entity_column=entity_column,
    )

    ranking = engine.rank()

    if clustering == "auto":
        ranking = cluster_from_ranking(ranking)

    return {
        "status": "OK",
        "ranking": ranking,
    }
