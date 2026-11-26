from ..schemas import canonical

def render(context):
    return ("Assess the parent independently. You may disagree, rewrite or invent an "
            "operator within this Worker turn.\n" + canonical(context))
