def anomalies(records):
    return [record["regression"] for record in records
            if record.get("regression") and record["regression"].get("category") is not None]
