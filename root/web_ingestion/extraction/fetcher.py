import requests

def fetch_html(url: str) -> str | None:
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; PVLBot/1.0)"
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        return resp.text
    except Exception:
        return None
