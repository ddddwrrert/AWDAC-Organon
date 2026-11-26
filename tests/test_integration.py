import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from awdac.integration.organon_adapter import snapshot, worker_context


class OriginalArtifactsTests(unittest.TestCase):
    def test_snapshot_read_only_and_unfinished_allocation(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)
            run = task / "run"
            (run / "evals").mkdir(parents=True)
            for identifier in ("c000000", "c000001", "c000009"):
                (run / "candidates" / identifier).mkdir(parents=True)
            (task / "task.json").write_text('{"program":"solution.py"}', encoding="utf-8")
            (run / "budget.json").write_text('{"max":100}', encoding="utf-8")
            source = run / "candidates/c000000/solution.py"
            source.write_text("def solve(): return 1", encoding="utf-8")
            rows = [{"id": "c000000", "parent": None, "fitness": 7, "survival": "yes"},
                    {"id": "c000001", "parent": "c000000", "fitness": 0, "survival": "no"}]
            (run / "population.jsonl").write_text("\n".join(map(json.dumps, rows)), encoding="utf-8")
            (run / "evals/c000000.json").write_text('{"fitness":7,"metrics":{}}', encoding="utf-8")

            def hashes():
                return {path: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in task.rglob("*") if path.is_file()}

            before = hashes()
            state = snapshot(task)
            self.assertEqual(state["budget"], {"max": 100, "used": 2, "remaining": 98})
            self.assertEqual(state["population"][1]["survival"], "no")
            self.assertIsNone(state["population"][1]["evaluation"])
            self.assertEqual(worker_context(task, "c000000")["capabilities"][0]["symbol"], "solve")
            self.assertEqual(hashes(), before)


    def test_ahc015_same_evaluation_and_structured_feedback(self):
        from enum import Enum
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch

        from awdac.enhancer import Enhancer
        from awdac.integration.evaluation_adapter import prepare_ahc015
        from awdac.integration.event_hooks import sync_run
        from awdac.memory import Memory
        from awdac.settings import load

        class JudgeResult(Enum):
            ACCEPTED = "AC"

        class Session:
            problem = SimpleNamespace(metadata=SimpleNamespace(score_type="minimize"))

            def case_gen(self, seeds):
                self.seeds = seeds
                return seeds

            def case_eval(self, cases, code, **options):
                calls.append(cases)
                rows = [SimpleNamespace(judge_result=JudgeResult.ACCEPTED,
                                        absolute_score=100 + seed - len(code),
                                        execution_time=0.1, memory_usage=1024,
                                        error_str="", message="") for seed in cases]
                return SimpleNamespace(case_results=rows, overall_judge_result=JudgeResult.ACCEPTED,
                                       overall_absolute_score=sum(row.absolute_score for row in rows))

            def close(self):
                pass

        calls = []
        results = ModuleType("ale_bench.result")
        results.CaseResult = results.Result = SimpleNamespace
        results.JudgeResult = JudgeResult
        session = ModuleType("ale_bench_eval.safe_ale_session")
        session.start_ale_bench_session = lambda **options: Session()
        original = Path(__file__).resolve().parents[1] / "Organon_original"
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "sys.modules", {results.__name__: results, session.__name__: session}
        ):
            task = prepare_ahc015(original, Path(directory) / "task")
            source = task / "evaluator/evaluator.py"
            scope = {"__name__": "instrumented_evaluator"}
            exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), scope)
            original_evaluator = original / "tasks/ale_bench/ahc015/evaluator/evaluator.py"
            baseline = {"__name__": "original_evaluator"}
            exec(compile(original_evaluator.read_text(encoding="utf-8"), str(original_evaluator), "exec"), baseline)
            rows = []
            for index, code in enumerate(("int x;", "int xyz;")):
                candidate = f"c{index:06}"
                parent = "c000000" if index else None
                program = task / "run/candidates" / candidate / "solution.cpp"
                program.parent.mkdir(parents=True)
                program.write_text(code, encoding="utf-8")
                before = len(calls)
                metrics = scope["evaluate"](program)
                self.assertEqual(len(calls), before + 1)
                self.assertEqual(calls[-1], list(range(50)))
                self.assertEqual(len(metrics["awdac"]["seeds"]), 50)
                self.assertEqual({k: v for k, v in metrics.items() if k != "awdac"},
                                 baseline["evaluate"](program))
                score = metrics["combined_score"]
                rows.append({"id": candidate, "parent": parent, "fitness": score})
                evaluation = task / "run/evals" / (candidate + ".json")
                evaluation.parent.mkdir(exist_ok=True)
                evaluation.write_text(json.dumps({"fitness": score, "metrics": metrics}))
            (task / "run/population.jsonl").write_text("\n".join(map(json.dumps, rows)))
            (task / "run/budget.json").write_text('{"max":100}')
            intent = task / "run/awdac/intents/c000001.json"
            intent.parent.mkdir(parents=True)
            intent.write_text(json.dumps({"parent": "c000000", "intent": {
                "mode": "radical", "hypothesis": "H", "observation": "O",
                "design": "D", "benefit": "B", "risk": "R", "validation": "V",
                "rebuttal": "Alternative", "operator_actions": ["create:move"],
            }}))
            with Memory(":memory:") as memory:
                enhancer = Enhancer(memory, load())
                self.assertEqual(sync_run(task, enhancer)["budget"]["used"], 1)
                self.assertEqual(sync_run(task, enhancer)["imported"], 2)
                record = memory.read_record(str(task), "c000001")
                self.assertEqual(record["intent"]["rebuttal"], "Alternative")
                self.assertEqual(record["paired"]["mean_delta"], 2)
                self.assertEqual(record["paired"]["unpaired"], 0)
