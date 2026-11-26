import unittest
from awdac.memory import Memory


class Verification(unittest.TestCase):
    def test_memory(self):
        with Memory(":memory:") as db:
            db.save("run", "child", "task", "parent", {}, "a", {}, {"program": {"source": "a"}})
            self.assertEqual(db.read_record("run", "child", "program"), {"source": "a"})
            with self.assertRaises(ValueError):
                db.save("run", "child", "task", "parent", {}, "b", {}, {})
            self.assertEqual(db.read_record("run", "child", "program"), {"source": "a"})
