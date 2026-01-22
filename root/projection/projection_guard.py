def validate_projection(
    df,
    required_columns: list[str],
):
    """
    Ensures user has not dropped required columns.
    """

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        return {
            "allowed": False,
            "reason": f"Required columns missing after projection: {missing}",
        }

    return {"allowed": True}
