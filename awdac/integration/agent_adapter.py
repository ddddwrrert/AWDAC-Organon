from .organon_adapter import snapshot

def agent_context(task_dir):
    state = snapshot(task_dir)
    return {"budget": state["budget"], "population": state["population"]}
