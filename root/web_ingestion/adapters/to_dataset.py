def to_dataset(rows, schema, intent):
    return {
        "rows": rows,
        "schema": schema,
        "metadata": {
            "source": "web",
            "entity": intent.entity,
            "geo": intent.geo,
            "confidence": 0.6
        }
    }
