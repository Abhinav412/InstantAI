from utils.llm import call_llm
from models.schema import TaskIntent


def infer_intent(query: str) -> TaskIntent:
    system = "You extract ranking intent. Return ONLY valid JSON."
    user = f"""
    Query: "{query}"

    Return JSON:
    task_type, entity_type, scope, top_k,
    ranking_nature, user_constraints
    """

    return TaskIntent(**call_llm(system, user))
