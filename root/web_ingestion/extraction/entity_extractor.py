import re


def extract_companies(text: str, tables=None, entity_type: str | None = None) -> list[dict]:
    """
    Generic entity extractor.
    Currently supports company extraction from text.
    """
    entities = set()

    if not text:
        return []

    # -------- Company extraction (text-first) --------
    if entity_type == "company":
        patterns = [
            r"\b[A-Z][A-Za-z& ]+(Limited|Ltd|Corporation|Corp|Industries)\b",
            r"\bReliance Industries\b",
            r"\bTata Consultancy Services\b",
            r"\bInfosys\b",
        ]

        for pattern in patterns:
            for match in re.findall(pattern, text):
                entities.add(match if isinstance(match, str) else match[0])

    return [{"name": name, "source": "google_web"} for name in entities]
