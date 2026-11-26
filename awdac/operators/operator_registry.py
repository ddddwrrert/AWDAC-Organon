from ..schemas import digest

def registry(operators):
    return {digest(operator): operator for operator in operators}
