def enforce_planner_gate(data_gaps: list[dict]):
    if not data_gaps:
        return {
            "allowed": False,
            "reason": "No known data gaps — planner locked",
        }

    return {"allowed": True}
