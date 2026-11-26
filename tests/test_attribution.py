import unittest
from awdac.evidence.contribution_attribution import attribution


class Verification(unittest.TestCase):
    def test_attribution(self):
        record = attribution("before", "after", None, None)
        self.assertIn("+after", record["diff"])
        self.assertEqual(record["causal_status"], "unverified")
