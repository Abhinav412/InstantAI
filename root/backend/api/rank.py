from fastapi import APIRouter, Query
from backend.storage.dataset_store import get_dataset
from ranking.run_ranking import run_safe_kpi_ranking

router = APIRouter()


@router.post("/rank")
def rank_dataset(
    dataset_id: str = Query(...),
    kpi: str = Query(...),
    entity_column: str = Query(...),
    cluster: str = Query("none"),
):
    df = get_dataset(dataset_id)

    return run_safe_kpi_ranking(
        df=df,
        kpi=kpi,
        entity_column=entity_column,
        clustering=cluster,
    )
