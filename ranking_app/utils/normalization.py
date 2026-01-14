import numpy as np

def normalize(value, direction="maximize"):
    if value is None:
        return 0.0

    value = float(value)

    if direction == "minimize":
        return 1 / (1 + value)

    return value
