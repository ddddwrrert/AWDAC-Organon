import unittest
from awdac.collaboration.worker_context import render
from awdac.collaboration.disagreement import disagreement


class Verification(unittest.TestCase):
    def test_collaboration(self):
        self.assertIn("independently", render({"advice": "retain"}))
        self.assertEqual(disagreement({"intent": {"rebuttal": "replace"}}), "replace")
