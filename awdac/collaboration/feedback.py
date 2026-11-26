def feedback(records):
    return [record for record in records if record.get("intent") or record.get("regression")]
