from dkl.enums import KnowledgeState

ALLOWED_TRANSITIONS = {
    KnowledgeState.INGESTED: KnowledgeState.PROFILED,
    KnowledgeState.PROFILED: KnowledgeState.SEMANTIC_MAPPED,
    KnowledgeState.SEMANTIC_MAPPED: KnowledgeState.TRUST_EVALUATED,
    KnowledgeState.TRUST_EVALUATED: KnowledgeState.INDEXED,
    KnowledgeState.INDEXED: KnowledgeState.READY,
}

def advance_state(current_state):
    return ALLOWED_TRANSITIONS[current_state]
