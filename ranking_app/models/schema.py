from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TaskIntent:
    task_type: str
    entity_type: str
    scope: str
    top_k: int
    ranking_nature: str
    user_constraints: Dict


@dataclass
class EntityDefinition:
    name: str
    includes: List[str]
    excludes: List[str]
    source: str
    discovery_required: bool


@dataclass
class GapAnalysis:
    can_rank_with_current_data: bool
    missing_information: List[str]
    requires_web_data: bool


@dataclass
class ExternalData:
    source: Optional[str]
    records: List[Dict]


@dataclass
class MetricDefinition:
    name: str
    weight: float
    description: str


@dataclass
class MetricSet:
    metrics: List[MetricDefinition]
    normalization: str
