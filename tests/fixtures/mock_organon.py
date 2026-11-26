import json

def create_artifacts(task):
    (task / "run/candidates/c000000").mkdir(parents=True)
    (task / "task.json").write_text(json.dumps({"program": "solution.py"}))
    (task / "run/budget.json").write_text(json.dumps({"max": 100}))
