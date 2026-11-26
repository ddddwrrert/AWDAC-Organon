def disagreement(record):
    intent = record.get("intent") or {}
    return intent.get("rebuttal") or None
