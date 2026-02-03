from typing import Optional
import re

from agents.intent_resolver import resolve_metric_from_intent


class CrawlIntent:
    def __init__(
        self,
        entity: str,
        geo: Optional[str] = None,
        metric: Optional[str] = None,
    ):
        self.entity = entity
        self.geo = geo
        self.metric = metric


def _infer_entity(user_query: str) -> str:
    q = user_query.lower()

    if "incubator" in q:
        return "incubator"
    if "startup" in q:
        return "startup"
    if "company" in q or "companies" in q:
        return "company"

    return "entity"


def _infer_geo(user_query: str) -> Optional[str]:
    match = re.search(r"\bin\s+([a-zA-Z ]+)", user_query)
    return match.group(1).strip() if match else None


def resolve_crawl_intent(user_query: str) -> CrawlIntent:
    """
    Conservative intent resolution.

    Metric resolution is attempted ONLY if allowed_metrics
    are explicitly provided elsewhere in the pipeline.

    Otherwise, metric remains None and DKL handles clarification.
    """

    entity = _infer_entity(user_query)
    geo = _infer_geo(user_query)

    # ⚠️ Under strict boundaries, web_ingestion does NOT
    # attempt metric resolution without DKL input.
    metric = resolve_metric_from_intent(
        user_query=user_query,
        allowed_metrics=[],   # intentionally empty
    )

    return CrawlIntent(
        entity=entity,
        geo=geo,
        metric=metric,
    )
