def retrieve(memory, task, context, current_run, limit=20):
    return [row for row in memory.history(task, context, limit, exclude_run=current_run)
            if row["record"].get("attribution")]
