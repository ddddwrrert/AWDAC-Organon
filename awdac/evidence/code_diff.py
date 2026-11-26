from difflib import unified_diff

def diff(parent, child):
    return "".join(unified_diff(parent.splitlines(keepends=True), child.splitlines(keepends=True),
                                fromfile="parent", tofile="child"))
