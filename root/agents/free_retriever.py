import requests


WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def fetch_from_wikipedia(entity: str, metric: str) -> list[dict]:
    """
    Fetches structured summaries from Wikipedia.
    Always treated as LOW TRUST.
    """
    query = f"{entity.replace(' ', '_')}"

    try:
        response = requests.get(
            WIKIPEDIA_API + query,
            timeout=10,
            headers={"User-Agent": "DKL-Free-Retriever/1.0"},
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    if "extract" not in data:
        return []

    return [
        {
            "source": "wikipedia",
            "title": data.get("title"),
            "snippet": data.get("extract"),
            "url": data.get("content_urls", {})
                         .get("desktop", {})
                         .get("page"),
        }
    ]


def fetch_public_sources(entity: str, metric: str) -> list[dict]:
    """
    Placeholder for open data portals / official sites.
    Extendable without architecture changes.
    """
    # For now, we only rely on Wikipedia
    return fetch_from_wikipedia(entity, metric)
