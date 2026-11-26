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
    def test_acu(self):
        report = profile(BASELINE, traces=["initialize"])
        self.assertEqual(report[0].status, "observed")
        self.assertEqual(report[1].dependencies, ("initialize",))
        self.assertEqual(changes(report, profile(OPERATOR))["added"], ["neighborhood"])
