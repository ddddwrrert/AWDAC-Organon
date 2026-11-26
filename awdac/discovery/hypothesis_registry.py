from ..schemas import digest

def registry(hypotheses):
    return {digest(item): item for item in hypotheses}
