def normalize_rows(rows):
    for r in rows:
        if "name" in r and isinstance(r["name"], str):
            r["name"] = r["name"].strip()
    return rows
