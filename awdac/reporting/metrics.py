from math import isfinite

def metrics(population):
    scores = [row.get("fitness") for row in population]
    valid = [score for score in scores if type(score) in (float, int) and isfinite(score)]
    return {"population_records": len(scores), "finite_scores": len(valid)}
