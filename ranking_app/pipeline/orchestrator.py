from pipeline.stage_01_intent import infer_intent
from pipeline.stage_02_entity import define_entity
from pipeline.stage_03_data_understanding import understand_data
from pipeline.stage_04_gap_analysis import analyze_gaps
from pipeline.stage_05_web_intelligence import fetch_external_data
from pipeline.stage_05_5_entity_extraction import extract_entities
from pipeline.stage_06_metric_constructor import construct_metrics
from pipeline.stage_07_signal_extraction import extract_signals
from pipeline.stage_08_scoring import score_entities
from pipeline.stage_09_explanation import explain
from utils.dedup import deduplicate_rankings


def run_pipeline(query, data=None):
    intent = infer_intent(query)
    entity_def = define_entity(intent)

    data_insights = understand_data(data)
    gap = analyze_gaps(intent, data_insights)

    external_data = fetch_external_data(gap, intent)

    entities = extract_entities(
        external_data.records,
        intent.entity_type
    )
    print("EXTRACTED ENTITIES:", entities)

    metrics = construct_metrics(intent, data_insights, external_data)

    for e in entities:
        e["signals"] = extract_signals(e, metrics)

    raw_rankings = score_entities(entities, metrics)
    rankings = deduplicate_rankings(raw_rankings, strategy="max")

    try:
        explanation = explain(rankings, metrics)
    except Exception as e:
        print("⚠️ Explanation failed, using fallback:", e)
        explanation = {
            "summary": "Rankings generated, but explanation unavailable",
            "top_drivers": [],
            "confidence_interpretation": "Explanation agent failed safely"
        }


    return rankings, explanation
