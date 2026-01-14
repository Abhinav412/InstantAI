def safe_json_load(text, retries=2):
    import json, re

    for _ in range(retries):
        try:
            return json.loads(text)
        except:
            # try to extract JSON block
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
    raise ValueError("Invalid JSON")
