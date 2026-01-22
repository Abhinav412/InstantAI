# source trust model
from dkl.enums import TrustLevel
from datetime import datetime


class SourceTrust:
    def __init__(
        self,
        source_id: str,
        source_type: str,
        trust_level: TrustLevel,
        confidence_score: float,
        cross_verified: bool,
        last_updated: str,
        known_biases: list[str] | None = None,
    ):
        self.source_id = source_id
        self.source_type = source_type
        self.trust_level = trust_level
        self.confidence_score = confidence_score
        self.cross_verified = cross_verified
        self.last_updated = last_updated
        self.known_biases = known_biases or []

    def is_stale(self, max_age_days: int = 365) -> bool:
        last = datetime.strptime(self.last_updated, "%Y-%m-%d")
        return (datetime.utcnow() - last).days > max_age_days

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "trust_level": self.trust_level.value,
            "confidence_score": self.confidence_score,
            "cross_verified": self.cross_verified,
            "last_updated": self.last_updated,
            "known_biases": self.known_biases,
        }
