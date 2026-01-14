from utils.llm import call_llm
from models.schema import EntityDefinition, TaskIntent


def define_entity(intent: TaskIntent) -> EntityDefinition:
    system = """
    You define entities.
    Return ONLY a single valid JSON OBJECT.
    Do NOT return a list.
    Do NOT include explanations.
    """

    user = f"""
    Entity type: {intent.entity_type}

    Return a JSON OBJECT with EXACT keys:
    {{
      "name": string,
      "includes": list of strings,
      "excludes": list of strings,
      "source": string,
      "discovery_required": boolean
    }}
    """

    response = call_llm(system, user)

    # ✅ Correct guard
    if not isinstance(response, dict):
        raise TypeError(
            f"EntityDefinition expects dict, got {type(response)}: {response}"
        )

    return EntityDefinition(**response)
