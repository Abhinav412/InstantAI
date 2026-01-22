def enforce_dkl_gate(knowledge_index: dict):
    if knowledge_index.get("knowledge_state") != "READY":
        return {
            "mode": "CLARIFICATION_ONLY",
            "reason": "DKL not READY"
        }
    return {"mode": "FULL_ACCESS"}
