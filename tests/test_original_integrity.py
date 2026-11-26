import unittest
from pathlib import Path
from scripts.check_integrity import verify


class Verification(unittest.TestCase):
    def test_original_integrity(self):
        root = Path(__file__).resolve().parents[1]
        verify(root / "Organon_original", root / "docs/original-sha256.json")
