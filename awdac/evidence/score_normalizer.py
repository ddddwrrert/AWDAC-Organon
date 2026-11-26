def merit(score, direction):
    if direction not in {"min", "max"}:
        raise ValueError("Unknown score direction")
    return score if direction == "max" else -score
