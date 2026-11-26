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
    def test_failure_classification(self):
        for status, expected in (("compile_error", "E1"), ("timeout", "E2"),
                                 ("invalid_output", "E3"), ("success", "E4"),
                                 ("budget_mismatch", "E5"), ("condition_mismatch", "E6"),
                                 ("unknown", None)):
            with self.subTest(status=status):
                self.assertEqual(diagnose(status, 0, 10, .25)["category"], expected)
