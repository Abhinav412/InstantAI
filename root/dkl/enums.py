from enum import Enum

class ProfileStatus(str, Enum):
    INCOMPLETE = "INCOMPLETE"
    COMPLETE = "COMPLETE"

class KnowledgeState(str, Enum):
    INGESTED = "INGESTED"
    PROFILED = "PROFILED"
    SEMANTIC_MAPPED = "SEMANTIC_MAPPED"
    TRUST_EVALUATED = "TRUST_EVALUATED"
    INDEXED = "INDEXED"
    READY = "READY"

class TrustLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
