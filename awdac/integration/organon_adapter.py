"""Read-only interface to source-confirmed Organon run artifacts."""
import json
import re
from pathlib import Path


CANDIDATE = re.compile(r"c[0-9]{6}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot(task_dir):
    task = Path(task_dir).resolve()
    run = task / "run"
    settings = read_json(task / "task.json")
    budget_file = run / "budget.json"
    population_file = run / "population.jsonl"
    population = (
        [json.loads(line) for line in population_file.read_text(encoding="utf-8").splitlines()
         if line.strip()] if population_file.exists() else [])
    candidate_dir = run / "candidates"
    allocated = sorted(path.name for path in candidate_dir.iterdir()
                       if path.is_dir() and not path.is_symlink() and CANDIDATE.fullmatch(path.name)
                       ) if candidate_dir.exists() else []
    budget = None
    if budget_file.exists():
        cap = read_json(budget_file)["max"]
        if type(cap) is not int or not 0 <= cap <= 2**53 - 1:
            raise ValueError("Invalid original budget cap")
        used = sum(name != "c000000" for name in allocated)
        budget = {"max": cap, "used": used, "remaining": max(cap - used, 0)}
    candidates = []
    for row in population:
        identifier = row["id"]
        if not CANDIDATE.fullmatch(identifier):
            raise ValueError(f"Invalid candidate ID {identifier!r}")
        root = (candidate_dir / identifier).resolve()
        source = (root / settings["program"]).resolve()
        if not source.is_relative_to(root) or not root.is_relative_to(candidate_dir.resolve()):
            raise ValueError("Candidate program escapes its directory")
        evaluation = run / "evals" / f"{identifier}.json"
        candidates.append({**row, "program": str(source),
                           "evaluation": read_json(evaluation) if evaluation.exists() else None})
    return {"backend": "organon-artifacts", "budget": budget,
            "allocated": allocated, "population": candidates}


def worker_context(task_dir, candidate_id):
    """Generate optional context for the already existing Worker call."""
    from dataclasses import asdict
    from ..acu import profile

    state = snapshot(task_dir)
    row = next(item for item in state["population"] if item["id"] == candidate_id)
    path = Path(row["program"])
    static_profile = []
    if path.suffix == ".py" and path.is_file():
        try:
            static_profile = [asdict(item) for item in profile(path.read_text(encoding="utf-8"))]
        except SyntaxError:
            pass
    return {"candidate": candidate_id, "budget": state["budget"], "fitness": row["fitness"],
            "evaluation": row["evaluation"], "capabilities": static_profile,
            "worker_prompt": "Assess the parent independently. If an Agent hypothesis is supplied, "
                             "you may rebut it and implement your alternative as one candidate. "
                             "Record your design, expected benefit, and risk in the existing reply."}
