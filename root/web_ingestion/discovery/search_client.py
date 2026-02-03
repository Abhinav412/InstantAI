import requests
from typing import List

GOOGLE_API_KEY = "AIzaSyDD0FJiU5s41SdG-oP7HKFQLBzW9KZkjYM"
GOOGLE_CX = "e6db2632698fb4225"


def search_urls(query: str, num: int = 5) -> List[str]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items", [])
    links = [item["link"] for item in items if "link" in item]

    print("[SEARCH] URLs:", links)
    return links
