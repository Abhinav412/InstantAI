def is_allowed(url: str) -> bool:
    banned = ["medium.com", "quora.com"]
    return not any(b in url for b in banned)
