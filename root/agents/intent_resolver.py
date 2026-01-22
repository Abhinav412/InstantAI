import re
from typing import List, Dict, Optional


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9_ ]+", " ", text.lower()).strip()


def tokenize(text: str) -> List[str]:
    return [t for t in normalize(text).split() if len(t) > 2]


def score_metric_intent(
    user_tokens: List[str],
    metric_id: str,
    metric_definition: str | None = None,
) -> int:
    """
    Scores how well a user query matches a metric using:
    - metric_id tokens
    - definition tokens (if present)
    """
    score = 0

    metric_tokens = tokenize(metric_id)

    definition_tokens = (
        tokenize(metric_definition)
        if metric_definition
        else []
    )

    for token in user_tokens:
        if token in metric_tokens:
            score += 3
        elif token in definition_tokens:
            score += 1

    return score


def resolve_metric_from_intent(
    user_query: str,
    allowed_metrics: List[str],
    semantic_registry: Dict[str, Dict] | None = None,
) -> Optional[str]:
    """
    Resolves the most likely metric purely from:
    - user query text
    - allowed metric names
    - optional semantic definitions

    Returns:
        metric_id or None (if ambiguous / unclear)
    """

    if not allowed_metrics:
        return None

    user_tokens = tokenize(user_query)

    scores: Dict[str, int] = {}

    for metric_id in allowed_metrics:
        metric_def = None

        if semantic_registry and metric_id in semantic_registry:
            metric_def = semantic_registry[metric_id].get("definition")

        score = score_metric_intent(
            user_tokens=user_tokens,
            metric_id=metric_id,
            metric_definition=metric_def,
        )

        if score > 0:
            scores[metric_id] = score

    if not scores:
        return None

    # Sort by score descending
    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    # Ambiguity guard: top two scores too close
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None

    return ranked[0][0]
