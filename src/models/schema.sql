CREATE TABLE IF NOT EXISTS review_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_name TEXT NOT NULL,
  customer_email TEXT NOT NULL,
  order_no TEXT NOT NULL,
  issue_type TEXT NOT NULL,
  issue_description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'PENDING',
  reviewer TEXT,
  review_note TEXT,
  created_at TEXT NOT NULL,
  reviewed_at TEXT,
  email_sent INTEGER NOT NULL DEFAULT 0,
  erp_written INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS job_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_name TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  message TEXT
);

CREATE INDEX IF NOT EXISTS idx_review_tasks_status ON review_tasks(status);
CREATE INDEX IF NOT EXISTS idx_review_tasks_created_at ON review_tasks(created_at);
