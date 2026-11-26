from .organon_adapter import snapshot

def evaluations(task_dir):
    return {row["id"]: row["evaluation"] for row in snapshot(task_dir)["population"]
            if row["evaluation"] is not None}


def prepare_ahc015(original, destination):
    """Copy the original task and expose the already-computed cases as metrics."""
    import hashlib
    from pathlib import Path
    from shutil import copytree

    original, destination = Path(original).resolve(), Path(destination).resolve()
    if destination.is_relative_to(original):
        raise ValueError("Use a task directory outside the original source tree")
    task = original / "tasks/ale_bench/ahc015"
    evaluator = task / "evaluator/evaluator.py"
    source = evaluator.read_text(encoding="utf-8")
    marker = '        return {\n            "judge_result": public_result.overall_judge_result.value,'
    if source.count(marker) != 1 or 'cases = session.case_gen(list(range(num_public_cases)))' not in source:
        raise ValueError("Unsupported AHC015 evaluator source")
    provenance = hashlib.sha256(evaluator.read_bytes() + (task / "task.json").read_bytes()).hexdigest()
    patch = """        try:
            from hashlib import sha256
            from json import dumps

            case_identity = sha256(dumps(cases, ensure_ascii=False).encode()).hexdigest()
            raw_cases = public_result.case_results
            seeds = {}
            if len(raw_cases) == num_public_cases:
                for seed, case in enumerate(raw_cases):
                    score = float(case.absolute_score)
                    if case.judge_result == JudgeResult.ACCEPTED and abs(score) < float("inf"):
                        seeds[str(seed)] = score
            awdac = {"condition": "ahc015:" + PROVENANCE + ":" + case_identity,
                     "direction": "max" if optim_factor == 1 else "min",
                     "seeds": seeds}
        except Exception:
            awdac = None
        return {
            "awdac": awdac,
            "judge_result": public_result.overall_judge_result.value,"""
    patched = source.replace(marker, patch.replace("PROVENANCE", repr(provenance)))
    compile(patched, str(evaluator), "exec")
    copytree(task, destination)
    (destination / "evaluator/evaluator.py").write_text(patched, encoding="utf-8")
    return destination
