from dataclasses import dataclass


@dataclass
class MetricProgram:
    name: str
    weight: float
    feature_name: str


def synthesize_metric_programs(intent, features):
    feature_names = [f.name for f in features]
    programs = []

    for metric, weight in intent.metrics.items():
        matches = [f for f in feature_names if metric in f]

        if not matches:
            continue

        programs.append(
            MetricProgram(
                name=metric,
                weight=weight,
                feature_name=matches[0]
            )
        )

    return programs
