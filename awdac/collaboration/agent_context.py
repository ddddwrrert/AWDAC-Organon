from ..schemas import canonical

def render(context):
    return "Review existing population evidence and offer optional advice.\n" + canonical(context)
