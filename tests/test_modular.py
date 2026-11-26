import json
from pathlib import Path
import unittest

from awdac.acu.behavior_analyzer import summarize
from awdac.acu.dependency_analyzer import dependencies
from awdac.memory import Memory
from awdac.memory.contribution_retrieval import retrieve
from awdac.memory.program_store import read


class ModularTests(unittest.TestCase):
    def test_profile_and_observed_trace(self):
        fixture = Path(__file__).with_name("fixtures") / "trace.json"
        trace = json.loads(fixture.read_text(encoding="utf-8-sig"))
        self.assertEqual(summarize([trace]), {"accepted": 1})
        self.assertEqual(dependencies("def helper(): pass\ndef solve(): helper()")["solve"],
                         ("helper",))

    def test_shared_store_and_cross_run_retrieval(self):
        context = {"task": "reference"}
        with Memory(":memory:") as memory:
            for run in ("prior", "current"):
                memory.save(run, "candidate", "reference", None, context, "code",
                            {"attribution": {"causal_status": "unverified"}},
                            {"program": {"source": "code"}})
            self.assertEqual(read(memory, "prior", "candidate"), {"source": "code"})
            self.assertEqual([row["run_id"] for row in
                              retrieve(memory, "reference", context, "current", limit=1)], ["prior"])
