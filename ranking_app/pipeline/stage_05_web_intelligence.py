import os
import requests
from models.schema import ExternalData

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def run_web_intelligence(queries):
    docs = []

    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("⚠️ Google Search API credentials mNissing")
        return docs

    try:
        for q in queries:
            params = {
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CSE_ID,
                "q": q,
                "num": 5
            }

            response = requests.get(GOOGLE_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            for item in items:
                docs.append({
                    "query": q,
                    "url": item.get("link"),
                    "content": item.get("snippet", "")
                })

    except Exception as e:
        print("⚠️ Web search failed:", e)

    return docs


def fetch_external_data(gap, intent) -> ExternalData:
    if not gap.requires_web_data:
        return ExternalData(source=None, records=[])

    queries = [
        f"top {intent.entity_type} in {intent.scope}",
        f"{intent.entity_type} ranking {intent.scope}"
    ]

    docs = run_web_intelligence(queries)

    # 🔥 HARD FALLBACK (MANDATORY)
    if not docs:
        print("⚠️ Using fallback seed data")
        docs = [
            {
                "query": intent.entity_type,
                "url": "https://www.ycombinator.com",
                "content": "Y Combinator is a top startup accelerator providing funding and mentorship."
            },
            {
                "query": intent.entity_type,
                "url": "https://www.techstars.com",
                "content": "Techstars runs accelerator programs globally including India."
            }
        ]

    return ExternalData(source="web", records=docs)
