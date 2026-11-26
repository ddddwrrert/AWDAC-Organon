def ancestry(rows, candidate):
    parents = {row["candidate"]: row["parent"] for row in rows}
    seen = set()
    while candidate is not None:
        if candidate in seen:
            raise ValueError("Cyclic lineage")
        seen.add(candidate)
        yield candidate
        candidate = parents.get(candidate)
