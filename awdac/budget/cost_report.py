def summarize(counts):
    return {key: counts.get(key, 0)
            for key in ("evaluation_calls", "evaluated_seeds", "cache_hits")}
