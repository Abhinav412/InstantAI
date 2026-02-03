def infer_schema(rows):
    schema = {}

    for row in rows:
        for k, v in row.items():
            if k not in schema:
                schema[k] = type(v).__name__

    return schema
