import pandas as pd

from ingestion.dataset_loader import load_dataset
from dkl.profiling.profiler import DataProfiler
from agents.context_agent import infer_dataset_context
from dkl.models.semantic_metric import SemanticMetric
from dkl.semantic_registry import SemanticRegistry
from dkl.models.knowledge_index import KnowledgeIndex
from dkl.state_machine import advance_state
from dkl.enums import KnowledgeState
from projection.columns_selector import drop_columns


def process_user_dataset(
    file_path: str | None,
    injected_df: pd.DataFrame | None = None,
    drop_columns_list: list[str] | None = None,
    required_columns: list[str] | None = None,
    dataset_origin: str = "user",
):
    # -------------------------------------------------
    # 1. Load dataset
    # -------------------------------------------------
    if injected_df is not None:
        original_df = injected_df.copy()
    elif file_path is not None:
        original_df = load_dataset(file_path)
    else:
        raise ValueError("Either file_path or injected_df must be provided")

    # -------------------------------------------------
    # 2. Projection (non-destructive)
    # -------------------------------------------------
    working_df = drop_columns(
        df=original_df,
        drop_columns=drop_columns_list or [],
        required_columns=required_columns or [],
    )

    # -------------------------------------------------
    # 3. STEP 1 — Profiling
    # -------------------------------------------------
    profiler = DataProfiler()
    profile = profiler.profile("user_dataset_v1", working_df)

    # -------------------------------------------------
    # 4. STEP 2 — Semantic inference (agentic)
    # -------------------------------------------------
    context = infer_dataset_context(
        working_df.head(5).to_dict()
    )

    registry = SemanticRegistry()

    # ---- Agent-proposed metrics (if any)
    for field, meaning in context.get("candidate_metrics", {}).items():
        ambiguities = context.get("ambiguity_flags", {}).get(field, [])

        metric = SemanticMetric(
            metric_id=field,
            source_field=field,
            entity=context.get("primary_entity"),
            definition=meaning,
            semantic_type="unknown",
            unit="unknown",
            time_scope="unknown",
            higher_is_better=True,
            comparable_across_entities=not bool(ambiguities),
            ambiguity_flags=ambiguities,
        )
        registry.register(metric)

    # -------------------------------------------------
    # 4B. OPTION A — NUMERIC FALLBACK METRICS (CRITICAL)
    # -------------------------------------------------
    if not registry.metrics:
        for col, dtype in working_df.dtypes.items():
            if dtype.kind in "if":  # int / float
                metric = SemanticMetric(
                    metric_id=col,
                    source_field=col,
                    entity=None,
                    definition=f"Numeric field {col}",
                    semantic_type="numeric",
                    unit="unknown",
                    time_scope="unknown",
                    higher_is_better=True,
                    comparable_across_entities=True,
                )
                registry.register(metric)

    # -------------------------------------------------
    # 5. Knowledge Index
    # -------------------------------------------------
    ki = KnowledgeIndex()
    ki.knowledge_state = advance_state(ki.knowledge_state)  # PROFILED
    ki.knowledge_state = advance_state(ki.knowledge_state)  # SEMANTIC_MAPPED

    ki.known_metrics = list(registry.get_allowed_metrics().keys())
    ki.data_gaps = list(registry.get_blocked_metrics().keys())

    # -------------------------------------------------
    # 6. STEP 3 — Source Trust Rule
    # -------------------------------------------------
    if dataset_origin == "user":
        low_trust_present = False
        ki.knowledge_state = KnowledgeState.TRUST_EVALUATED
        ki.knowledge_state = KnowledgeState.READY
    else:
        low_trust_present = True

    return {
        "profile": profile.to_dict(),
        "knowledge_index": ki.to_dict(),
        "allowed_metrics": ki.known_metrics,
        "blocked_metrics": ki.data_gaps,
        "low_trust_present": low_trust_present,
    }
