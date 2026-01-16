import pandas as pd
from pipeline.stage_01_intent import parse_ranking_intent
from pipeline.stage_02_data_audit import audit_dataset
from pipeline.stage_02_semantic import explain_columns
from pipeline.stage_03_features import define_features
from pipeline.stage_03_transform import apply_feature_transforms


if __name__ == "__main__":

    query = (
        "Rank universities based on research output (40%), "
        "teaching quality (30%), and placements (30%)."
    )

    intent = parse_ranking_intent(query)

    audit = audit_dataset(
        file_path="sample_data.csv",
        entity_column=intent.entity_column
    )

    semantics = explain_columns(audit)

    features = define_features(audit, semantics)

    df = pd.read_csv("sample_data.csv")
    feature_df = apply_feature_transforms(df, features.features)

    print("\nFEATURE DEFINITIONS\n")
    for f in features.features:
        print(f.feature_name, "->", f.transform)

    print("\nFEATURE VALUES\n")
    print(feature_df)

from pipeline.stage_04_metric_map import map_metrics_to_features


metric_map = map_metrics_to_features(intent, features)

print("\nMETRIC → FEATURE MAP\n")
for metric, feats in metric_map.metric_to_features.items():
    print(metric, "->", feats)

from InstantAI.dataset_ranking_app.pipeline.stage_06_scoring import score_entities

scored = score_entities(
    df_raw=df,
    feature_df=feature_df,
    intent=intent,
    metric_map=metric_map
)

print("\nFINAL RANKINGS\n")
for rank, s in enumerate(scored, start=1):
    print(
        f"{rank}. {s.entity} | Score: {s.score} | "
        f"Breakdown: {s.metric_breakdown}"
    )

from InstantAI.dataset_ranking_app.pipeline.stage_08_explain import explain_ranking

explanation = explain_ranking(scored, intent)

print("\nRANKING EXPLANATION\n")
print("Summary:", explanation.summary)

print("\nTop Drivers:")
for d in explanation.top_drivers:
    print("-", d)

print("\nCaveats:")
for c in explanation.caveats:
    print("-", c)
