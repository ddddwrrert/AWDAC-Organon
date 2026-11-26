def evaluate_reference(memory, candidate, condition, evaluator, counts, *, reuse=False):
    result = memory.get_evaluation(candidate.source, condition) if reuse else None
    if result is not None:
        counts["cache_hits"] += 1
        return result
    counts["evaluation_calls"] += 1
    result = evaluator(candidate.source, condition)
    counts["evaluated_seeds"] += len(result["seeds"])
    if reuse:
        memory.save_evaluation(candidate.source, condition, result)
    return result
