CREATE TABLE IF NOT EXISTS experiments (
  run_id TEXT NOT NULL,
  candidate TEXT NOT NULL,
  task TEXT NOT NULL,
  parent TEXT,
  context TEXT NOT NULL,
  program_hash TEXT NOT NULL,
  record TEXT NOT NULL,
  PRIMARY KEY (run_id, candidate)
);
CREATE INDEX IF NOT EXISTS experiments_task ON experiments(task);
CREATE TABLE IF NOT EXISTS knowledge (
  run_id TEXT NOT NULL,
  candidate TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('program', 'algorithm', 'counterexample')),
  record TEXT NOT NULL,
  PRIMARY KEY (run_id, candidate, kind),
  FOREIGN KEY (run_id, candidate) REFERENCES experiments(run_id, candidate)
);
CREATE TABLE IF NOT EXISTS evaluations (
  identity TEXT PRIMARY KEY,
  condition TEXT NOT NULL,
  program_hash TEXT NOT NULL,
  result TEXT NOT NULL
);
PRAGMA user_version = 1;
