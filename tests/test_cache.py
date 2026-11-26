import unittest
from dataclasses import asdict, replace

from awdac.acu import changes, profile
from awdac.evidence import diagnose, paired
from awdac.learning import discover, implement_reference_operator, reliability
from awdac.memory import Memory
from awdac.schemas import Condition, Seed
from awdac.reference import BASELINE, OPERATOR

CONDITION = Condition("task", "eval", "env", "args", "protocol", (0, 1), "min")


class UnitTests(unittest.TestCase):
    def test_cache_identity(self):
        result = {"status": "success", "fitness": 1,
                  "seeds": [asdict(Seed(seed, 1, feasible=True)) for seed in CONDITION.seeds]}
        with Memory(":memory:") as db:
            db.save_evaluation(BASELINE, CONDITION, result)
            self.assertEqual(db.get_evaluation(BASELINE, CONDITION), result)
            self.assertIsNone(db.get_evaluation(OPERATOR, CONDITION))
            for field, value in (("environment", "new"), ("seeds", (1, 0)),
                                 ("purpose", "diagnostic"), ("parameters", "new")):
                self.assertIsNone(db.get_evaluation(BASELINE, replace(CONDITION, **{field: value})))
