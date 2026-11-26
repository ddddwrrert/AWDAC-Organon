import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from ..schemas import canonical, digest
from ..budget.cache_key import cache_key


class Memory:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys = ON")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1):
            self.db.close()
            raise ValueError(f"Unsupported schema version {version}")
        self.db.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.db.close()

    def save(self, run_id, candidate, task, parent, context, source, record, knowledge):
        with self.db:
            self.db.execute("""INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id,candidate) DO UPDATE SET record=excluded.record
                WHERE experiments.program_hash=excluded.program_hash
                  AND experiments.context=excluded.context
                  AND experiments.parent IS excluded.parent""",
                            (run_id, candidate, task, parent, canonical(context),
                             digest(source), canonical(record)))
            if not self.db.execute("SELECT changes()").fetchone()[0]:
                raise ValueError("Candidate identity conflicts with persisted lineage")
            self.db.execute("DELETE FROM knowledge WHERE run_id=? AND candidate=?",
                            (run_id, candidate))
            self.db.executemany("INSERT INTO knowledge VALUES (?, ?, ?, ?)",
                                [(run_id, candidate, kind, canonical(value))
                                 for kind, value in knowledge.items()])

    def history(self, task, context, limit=20, exclude_run=None):
        """CLR/CEL retrieval with exact context ranked before related same-task experience."""
        rows = self.db.execute("""
            SELECT candidate, parent, context, record, run_id FROM experiments
            WHERE task=? AND (? IS NULL OR run_id != ?) ORDER BY (context=?) DESC, rowid DESC LIMIT ?
        """, (task, exclude_run, exclude_run, canonical(context), limit))
        return [{"candidate": candidate, "parent": parent, "same_context": saved == canonical(context),
                 "context": json.loads(saved), "record": json.loads(record), "run_id": run_id}
                for candidate, parent, saved, record, run_id in rows]

    def get_evaluation(self, source, condition):
        identity = cache_key(source, condition)
        row = self.db.execute("SELECT result FROM evaluations WHERE identity=?", (identity,)).fetchone()
        return json.loads(row[0]) if row else None

    def save_evaluation(self, source, condition, result):
        from ..schemas import Seed

        rows = [Seed(**row) for row in result["seeds"]]
        if result["status"] != "success" or tuple(row.id for row in rows) != condition.seeds:
            return
        if any(row.status != "success" or row.feasible is not True or row.score is None
               for row in rows):
            return
        program_hash = digest(source)
        serialized = asdict(condition)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO evaluations VALUES (?, ?, ?, ?)",
                            (cache_key(source, condition), canonical(serialized),
                             program_hash, canonical(result)))

    def read_record(self, run_id, candidate, kind=None):
        if kind is None:
            row = self.db.execute("SELECT record FROM experiments WHERE run_id=? AND candidate=?",
                                  (run_id, candidate)).fetchone()
        else:
            row = self.db.execute("SELECT record FROM knowledge WHERE run_id=? AND candidate=? AND kind=?",
                                  (run_id, candidate, kind)).fetchone()
        return json.loads(row[0]) if row else None
