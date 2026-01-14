from utils.llm import call_llm

def extract_entities(documents, entity_type):
    system = """
    You extract real-world entities from text.
    Return ONLY valid JSON.
    """

    user = f"""
    Entity type: {entity_type}

    Documents:
    {documents}

    Return JSON array of objects:
    [
      {{
        "name": string,
        "url": string,
        "evidence": string
      }}
    ]
    """

    response = call_llm(system, user)

    if not isinstance(response, list):
        raise TypeError("Entity extraction must return a list")

    return response
