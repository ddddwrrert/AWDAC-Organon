from pathlib import Path
import json
import tomllib

def load(path=None):
    path = Path(path or Path(__file__).with_name("default.toml"))
    if path.suffix != ".yaml":
        with path.open("rb") as stream:
            return tomllib.load(stream)
    config = json.loads(path.read_text(encoding="utf-8"))
    config["evidence"] = json.loads(path.with_name("evidence.yaml").read_text(encoding="utf-8"))
    budget = json.loads(path.with_name("budget.yaml").read_text(encoding="utf-8"))
    if budget["formal"] != {"candidate_budget": 100, "replace_evaluation_from_cache": False}:
        raise ValueError("Formal budget and evaluator settings must follow Organon")
    config["features"]["reuse"] = budget["reference"]["reuse"]
    ablation = path.with_name("ablation.yaml")
    config["ablation"] = json.loads(ablation.read_text(encoding="utf-8"))["profiles"]
    return config
