import math
import statistics
from dataclasses import asdict


def paired(parent, child, condition, child_condition):
    if condition != child_condition:
        raise ValueError("Cannot pair across evaluation conditions")
    left, right = ({row.id: row for row in rows} for rows in (parent, child))
    if len(left) != len(parent) or len(right) != len(child):
        raise ValueError("Duplicate seed in evaluation")
    if set(left).union(right).difference(condition.seeds):
        raise ValueError("Unexpected seed")
    sign = 1 if condition.direction == "max" else -1
    pairs = []
    for seed in condition.seeds:
        first, second = left.get(seed), right.get(seed)
        if any(row is None or row.status != "success" or row.feasible is False
               or row.score is None or not math.isfinite(row.score) for row in (first, second)):
            continue
        delta = sign * (second.score - first.score)
        pairs.append({"seed": seed, "parent": asdict(first), "child": asdict(second),
                      "delta": delta,
                      "relative": delta / abs(first.score) if abs(first.score) >= 1e-9 else None,
                      "instance_features_missing": not bool(second.features or first.features)})
    deltas = [pair["delta"] for pair in pairs]
    mean = statistics.mean(deltas) if deltas else None
    sd = statistics.stdev(deltas) if len(deltas) > 1 else None
    return {"pairs": pairs, "mean_delta": mean, "sample_sd": sd,
            "standard_error": sd / math.sqrt(len(deltas)) if sd is not None else None,
            "unpaired": len(condition.seeds) - len(pairs)}


def diagnose(status, fitness, previous, collapse_fraction, capability_changes=None):
    failures = {"compile_error": "E1", "runtime_error": "E2", "timeout": "E2",
                "invalid_output": "E3", "invalid_constraints": "E3",
                "budget_mismatch": "E5", "condition_mismatch": "E6"}
    category = failures.get(status)
    if status == "success" and previous is not None and fitness is not None:
        if fitness < previous - abs(previous) * collapse_fraction:
            category = "E4"
    return {"category": category, "status": status,
            "capability_changes": capability_changes, "fitness": fitness}


def attribution(parent_source, child_source, intent, evidence):
    from difflib import unified_diff

    return {"diff": list(unified_diff(parent_source.splitlines(), child_source.splitlines(),
                                      fromfile="parent", tofile="child", lineterm="")),
            "hypothesis": intent.hypothesis if intent else None,
            "paired_seeds": len(evidence["pairs"]) if evidence else 0,
            "mean_delta": evidence["mean_delta"] if evidence else None,
            "causal_status": "unverified"}
