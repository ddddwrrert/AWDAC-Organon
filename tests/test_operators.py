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
    def test_operator_composition(self):
        from awdac.reference import evaluate

        source = implement_reference_operator("neighborhood", "max(values[0], pick(values))",
                                              "def pick(values): return max(values[1:])")
        scores = evaluate(source, CONDITION)
        self.assertEqual(scores["fitness"], evaluate(OPERATOR, CONDITION)["fitness"])
