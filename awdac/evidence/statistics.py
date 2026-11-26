from statistics import mean, stdev
from math import sqrt

def summarize(values):
    return {"count": len(values), "mean": mean(values) if values else None,
            "standard_error": stdev(values) / sqrt(len(values)) if len(values) > 1 else None}
