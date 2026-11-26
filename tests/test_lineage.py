import unittest
from awdac.memory.lineage import ancestry


class Verification(unittest.TestCase):
    def test_lineage(self):
        rows = [{"candidate": "b", "parent": "a"}, {"candidate": "a", "parent": None}]
        self.assertEqual(list(ancestry(rows, "b")), ["b", "a"])
        with self.assertRaises(ValueError):
            list(ancestry([{"candidate": "a", "parent": "a"}], "a"))
