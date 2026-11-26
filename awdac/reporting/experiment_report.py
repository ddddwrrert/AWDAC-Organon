from ..schemas import canonical
from ..integration.organon_adapter import snapshot

from .metrics import metrics

def report(task_dir):
    state = snapshot(task_dir)
    return canonical({**state, "metrics": metrics(state["population"])})
