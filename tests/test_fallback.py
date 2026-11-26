import unittest
from fixtures.sample_evaluations import CONDITION
from fixtures.sample_programs import INVALID
from awdac.reference import evaluate


class Verification(unittest.TestCase):
    def test_fallback(self):
        self.assertEqual(evaluate("def solve(:", CONDITION)["status"], "compile_error")
        self.assertEqual(evaluate("def solve(values): 1/0", CONDITION)["status"], "runtime_error")
        self.assertEqual(evaluate(INVALID, CONDITION)["status"], "invalid_output")
