def coverage(seeds):
    return {"total": len(seeds), "feasible": sum(seed.feasible is True for seed in seeds),
            "scored": sum(seed.score is not None for seed in seeds)}
