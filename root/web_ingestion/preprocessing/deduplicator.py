def deduplicate(rows):
    seen = set()
    unique = []

    for r in rows:
        key = r.get("name")
        if key and key not in seen:
            seen.add(key)
            unique.append(r)

    return unique
