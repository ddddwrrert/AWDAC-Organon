from .agent_adapter import agent_context
from .evaluation_adapter import evaluations
from .worker_adapter import worker_context

class ArtifactHooks:
    def __init__(self, task_dir):
        self.task_dir = task_dir

    def after_batch(self):
        return agent_context(self.task_dir)

    def before_worker(self, parent_id):
        return worker_context(self.task_dir, parent_id)

    def after_evaluation(self, candidate_id):
        return evaluations(self.task_dir).get(candidate_id)


def sync_run(task_dir, enhancer):
    """Import completed official artifacts and produce context for an existing Agent turn."""
    from dataclasses import fields
    import json
    from pathlib import Path

    from .organon_adapter import snapshot
    from ..schemas import Candidate, Condition, Intent

    task = Path(task_dir).resolve()
    state = snapshot(task)
    programs = {}
    conditions = {}
    results = {}
    latest = None
    for row in state["population"]:
        identifier = row["id"]
        path = Path(row["program"])
        result = row["evaluation"]
        if not result or not path.is_file():
            continue
        metrics = result.get("metrics") or {}
        packet = metrics.get("awdac") or result.get("awdac") or {}
        parent_id = row.get("parent")
        intent = None
        try:
            capture = json.loads((task / f"run/awdac/intents/{identifier}.json").read_text(encoding="utf-8"))
            raw = capture["intent"]
            if capture["parent"] == parent_id and all(
                isinstance(raw.get(field.name, ""), str) for field in fields(Intent)
                if field.name != "operator_actions"
            ):
                actions = raw.get("operator_actions", [])
                if isinstance(actions, list) and all(isinstance(action, str) for action in actions):
                    intent = Intent(**{**raw, "operator_actions": tuple(actions)})
        except (ValueError, OSError, KeyError, TypeError, AttributeError):
            pass
        verdict = str(metrics.get("judge_result", "")).lower()
        status = {"ac": "success", "accepted": "success", "ce": "compile_error",
                  "tle": "timeout", "wa": "invalid_output", "re": "runtime_error"}.get(verdict, "unknown")
        condition = Condition("ahc015", packet.get("condition", "legacy"),
                              str(task), "lite-cpp20", "public-mean-50",
                              tuple(range(50)), packet.get("direction", "max"))
        observation = {"fitness": result["fitness"], "status": status, "seeds": [
            {"id": int(seed), "score": score, "feasible": True}
            for seed, score in (packet.get("seeds") or {}).items()
        ]}
        candidate = Candidate(path.read_text(encoding="utf-8"), intent)
        comparable = conditions.get(parent_id) == condition
        enhancer.feedback(str(task), identifier, candidate, condition, observation,
                          parent_id, programs.get(parent_id),
                          results.get(parent_id) if comparable else None)
        programs[identifier], conditions[identifier], results[identifier] = candidate, condition, observation
        latest = identifier
    return {"backend": "organon-ahc015", "budget": state["budget"], "imported": len(programs),
            "agent_context": enhancer.context(
                programs[latest].source, programs.get("c000000", programs[latest]).source,
                conditions[latest], state["population"][-10:]
            ) if latest is not None else None}
