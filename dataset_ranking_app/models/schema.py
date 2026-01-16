from dataclasses import dataclass
from typing import List


@dataclass
class MetricIntent:
    name: str
    weight: float


@dataclass
class RankingIntent:
    entity_column: str
    metrics: List[MetricIntent]
    direction: str

from typing import Dict, Any


@dataclass
class ColumnProfile:
    dtype: str
    missing_ratio: float


@dataclass
class DatasetAudit:
    entity_column: str
    columns: Dict[str, ColumnProfile]
    column_semantics: Dict[str, str]

from typing import List, Optional


@dataclass
class FeatureDefinition:
    feature_name: str
    source_columns: List[str]
    transform: Optional[str]
    description: str


@dataclass
class FeatureSet:
    features: List[FeatureDefinition]

@dataclass
class FeatureDefinition:
    feature_name: str
    source_columns: List[str]
    transform: Optional[str]   # log | inverse | None | formula
    formula: Optional[str]     # explicit math expression
    description: str

from typing import Dict, List


@dataclass
class MetricFeatureMap:
    metric_to_features: Dict[str, List[str]]

from typing import Dict


@dataclass
class ScoredEntity:
    entity: str
    score: float
    metric_breakdown: Dict[str, float]

from typing import List


@dataclass
class RankingExplanation:
    summary: str
    top_drivers: List[str]
    caveats: List[str]
