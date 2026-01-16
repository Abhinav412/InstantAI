import re
from utils.llm import call_llm


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def resolve_entity_column(intent_col, audit):
    norm_cols = {normalize(c): c for c in audit.df.columns}
    key = normalize(intent_col)

    if key in norm_cols:
        return norm_cols[key]

    for c in audit.text_columns:
        if "id" in c.lower() or "name" in c.lower():
            return c

    return audit.text_columns[0]


def map_metrics_to_features(intent, audit, features):
    resolved = {}

    norm_numeric = {normalize(c): c for c in audit.numeric_columns}

    for metric, weight in intent.metrics.items():
        mkey = normalize(metric)

        # 1️⃣ Exact / substring match
        matched = None
        for nkey, col in norm_numeric.items():
            if nkey in mkey or mkey in nkey:
                matched = col
                break

        if matched:
            resolved[matched] = weight
            continue

        # 2️⃣ LLM SEMANTIC FALLBACK (CRITICAL)
        system = """
        You map a ranking metric to a dataset column.
        Return ONLY JSON.
        """

        user = f"""
        Metric: {metric}

        Available numeric columns:
        {audit.numeric_columns}

        Return JSON:
        {{ "column": "best_matching_column" }}
        """

        result = call_llm(system, user)
        column = result.get("column")

        if column not in audit.numeric_columns:
            raise ValueError(
                f"Metric '{metric}' could not be mapped to any column"
            )

        resolved[column] = weight

    return resolved
