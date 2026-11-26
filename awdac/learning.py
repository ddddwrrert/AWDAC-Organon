import ast


def implement_reference_operator(name, expression, components=""):
    """M3 reference implementation: assemble a named operator and a solver call."""
    if not name.isidentifier() or name == "solve":
        raise ValueError("Invalid operator name")
    body = ast.parse(expression, mode="eval")
    source = (
        f"{components.rstrip()}\n\n" if components.strip() else ""
    ) + f"def {name}(values):\n    return {ast.unparse(body)}\n\ndef solve(values):\n    return {name}(values)\n"
    compile(source, "<reference operator>", "exec")
    return source


def discover(profile, history, observations=()):
    """M9/M2 surface unresolved observations, including caller-supplied novel dimensions."""
    signals = list(observations)
    failures = [item for item in history if item["same_context"]
                and (item["record"].get("regression") or {}).get("category") == "E4"]
    if len(failures) >= 2:
        signals.append({"dimension": "rewrite quality", "detail": "Repeated E4 in this context"})
    symbols = [item.symbol for item in profile if item.role == "neighborhood"]
    return [{"observation": item, "operator_symbols": symbols,
             "hypothesis": f"Investigate whether {item['dimension']} limits solution quality",
             "status": "hypothesized"} for item in signals]


def reliability(history):
    """M7 counts directional outcomes from actual comparable experiments."""
    counts = {}
    seen = set()
    for item in history:
        record = item["record"]
        intent = record.get("intent")
        scores = record.get("paired")
        if not item["same_context"] or not intent or not scores or scores["unpaired"]:
            continue
        key = (intent["hypothesis"], record.get("comparison_id"))
        if key in seen:
            continue
        seen.add(key)
        delta = scores["mean_delta"]
        if delta is None:
            continue
        bucket = counts.setdefault(intent["hypothesis"], {"positive": 0, "negative": 0, "tie": 0})
        bucket["positive" if delta > 0 else "negative" if delta < 0 else "tie"] += 1
    return counts


def operator_feedback(capability_changes, intent, evidence):
    """M4 records co-occurring changes without claiming isolated contributions."""
    if not intent or not intent.operator_actions:
        return None
    return {"actions": list(intent.operator_actions), "symbols": capability_changes,
            "paired_mean": evidence["mean_delta"] if evidence else None,
            "causal_status": "unverified"}
