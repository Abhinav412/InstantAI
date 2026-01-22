from dkl.enums import KnowledgeState

class KnowledgeIndex:
    def __init__(self):
        self.knowledge_state = KnowledgeState.INGESTED
        self.known_entities = []
        self.known_metrics = []
        self.data_gaps = []

    def to_dict(self):
        return {
            "knowledge_state": self.knowledge_state.value,
            "known_entities": self.known_entities,
            "known_metrics": self.known_metrics,
            "data_gaps": self.data_gaps
        }
    def update_known_metrics(self, semantic_registry):
        self.known_metrics = list(
            semantic_registry.get_allowed_metrics().keys()
        )
    def mark_trust_evaluated(self):
        from dkl.enums import KnowledgeState
        self.knowledge_state = KnowledgeState.TRUST_EVALUATED
