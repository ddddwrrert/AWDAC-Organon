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
    def test_pairing(self):
        report = paired([Seed(0, 5)], [Seed(0, 2)], CONDITION, CONDITION)
        self.assertEqual(report["mean_delta"], 3)
        self.assertEqual(report["unpaired"], 1)
        with self.assertRaises(ValueError):
            paired([], [], CONDITION, replace(CONDITION, evaluator="other"))
