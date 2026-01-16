def generate_features(audit):
    features = {}

    for col in audit.numeric_columns:
        features[col] = col
        features[f"log_{col}"] = f"log({col})"
        features[f"inverse_{col}"] = f"1/{col}"

    # cross features
    for c1 in audit.numeric_columns:
        for c2 in audit.numeric_columns:
            if c1 != c2:
                features[f"{c1}_per_{c2}"] = f"{c1}/{c2}"

    return features
