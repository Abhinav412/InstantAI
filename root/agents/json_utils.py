import json
import re


def extract_json(text: str) -> dict:
    """
    Safely extracts the first JSON object from an LLM response.
    Raises ValueError if no valid JSON is found.
    """

    if not text:
        raise ValueError("Empty LLM response")

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")

    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError("Extracted JSON is invalid") from e
