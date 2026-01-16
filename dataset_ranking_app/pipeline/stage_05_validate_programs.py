def validate_programs(programs, features):
    feature_map = {f.name: f.series for f in features}

    valid = []

    for p in programs:
        if p.feature_name in feature_map:
            valid.append((p, feature_map[p.feature_name]))

    return valid
