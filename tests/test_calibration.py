import unittest
from awdac.discovery.evidence_calibration import reliability


class Verification(unittest.TestCase):
    def test_calibration(self):
        observation = {"same_context": True, "record": {"intent": {"hypothesis": "H"},
                       "comparison_id": "X", "paired": {"unpaired": 0, "mean_delta": -1}}}
        self.assertEqual(reliability([observation, observation])["H"]["negative"], 1)
        self.assertFalse(reliability([{**observation, "same_context": False}]))
