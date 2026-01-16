from utils.llm import call_llm

def extract_entities(documents, entity_type):
    system = """
    You are an entity extraction agent.

    STRICT RULES:
    - Return ONLY a JSON array (list)
    - Do NOT include explanations
    - Do NOT include markdown
    - Do NOT include comments
    - Each item must have: name, url, evidence
    - Return [] if no entities are found
    """

    user = f"""
    Entity type: {entity_type}

    Documents:
    {documents}

    Return EXACTLY this structure:

    [
      {{
        "name": string,
        "url": string,
        "evidence": string
      }}
    ]
    """

    response = call_llm(system, user)

    # -------- SAFE NORMALIZATION (CRITICAL) --------

    # Case 1: Perfect
    if isinstance(response, list):
        return response

    # Case 2: Wrapped list
    if isinstance(response, dict) and "entities" in response:
        if isinstance(response["entities"], list):
            return response["entities"]

    # Case 3: Single entity object
    if isinstance(response, dict) and {"name", "url", "evidence"} <= response.keys():
        return [response]

    # Case 4: Anything else → recover safely
    print("⚠️ Entity extraction malformed response:", response)
    return []
