import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


class EndToEndTests(unittest.TestCase):
    def test_cli_and_persisted_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.sqlite"
            output = subprocess.check_output(
                [sys.executable, "-B", "-m", "awdac", "demo", "--db", str(path)], text=True)
            result = json.loads(output)
            self.assertEqual(result["budget"]["used"], 3)
            self.assertEqual(result["cost"]["evaluation_calls"], 2)
            self.assertEqual(result["cost"]["cache_hits"], 2)
            self.assertGreater(result["best_fitness"], result["population"][0]["fitness"])
            with closing(sqlite3.connect(path)) as db:
                record = json.loads(db.execute(
                    "SELECT record FROM experiments WHERE candidate='c000001'").fetchone()[0])
            self.assertEqual(record["intent"]["mode"], "radical")
            self.assertTrue(record["intent"]["rebuttal"])
            self.assertEqual(record["operator"]["causal_status"], "unverified")
            self.assertEqual(record["paired"]["unpaired"], 0)
