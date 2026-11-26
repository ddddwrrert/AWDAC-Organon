import unittest
from awdac.discovery.bottleneck_discovery import discover


class Verification(unittest.TestCase):
    def test_discovery(self):
        signals = discover([], [], [{"dimension": "new representation"}])
        self.assertIn("new representation", signals[0]["hypothesis"])
