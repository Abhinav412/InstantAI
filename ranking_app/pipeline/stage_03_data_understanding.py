def understand_data(data):
    if not data:
        return {"available": False, "record_count": 0}

    return {
        "available": True,
        "record_count": len(data),
        "fields": list(data[0].keys()) if data else []
    }
