import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from fixtures.mock_organon import create_artifacts
from awdac.integration.organon_adapter import snapshot


class Verification(unittest.TestCase):
    def test_budget(self):
        with TemporaryDirectory() as tmp:
            create_artifacts(Path(tmp))
            self.assertEqual(snapshot(tmp)["budget"], {"max": 100, "used": 0, "remaining": 100})
