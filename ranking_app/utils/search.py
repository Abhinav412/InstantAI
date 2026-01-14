# utils/search.py
import requests
from bs4 import BeautifulSoup

def duckduckgo_search(query, max_results=5):
    url = "https://duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {"q": query}

    r = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for a in soup.select(".result__a")[:max_results]:
        results.append({
            "title": a.get_text(),
            "url": a.get("href")
        })

    return results
