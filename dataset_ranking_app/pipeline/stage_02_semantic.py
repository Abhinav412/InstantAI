from utils.llm import call_llm


def explain_columns(dataset_audit):
    system = """
    You are a data analyst.

    RULES:
    - Return ONLY valid JSON.
    - Do NOT describe statistics.
    - Focus on what each column represents.
    """

    column_names = list(dataset_audit.columns.keys())

    user = f"""
    Dataset columns:
    {column_names}

    Entity column:
    {dataset_audit.entity_column}

    Return JSON mapping column_name -> description.
    """

    return call_llm(system, user)

