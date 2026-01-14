from utils.llm import call_llm
from models.schema import GapAnalysis


def analyze_gaps(intent, data_insights) -> GapAnalysis:
    system = "You analyze gaps. Return ONLY valid JSON."
    user = f"""
    Intent: {intent}
    Data: {data_insights}

    Return JSON:
    can_rank_with_current_data (bool),
    missing_information (list),
    requires_web_data (bool)
    """

    return GapAnalysis(**call_llm(system, user))
