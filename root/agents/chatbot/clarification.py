def build_clarification_response(
    allowed_metrics: list[str],
    blocked_metrics: list[str],
):
    if allowed_metrics:
        return (
            "How would you like to rank the companies? "
            "For example: " + ", ".join(allowed_metrics[:5])
        )

    if blocked_metrics:
        return (
            "I found possible ranking metrics, but they are ambiguous: "
            + ", ".join(blocked_metrics)
            + ". Could you clarify?"
        )

    return (
        "I need more information to rank the companies. "
        "Please specify a ranking criterion."
    )
