import sqlite3
from datetime import datetime
import os

class Storage:
    def __init__(self, db_path="data/jobs.db"):
        self.db_path = db_path

        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    link TEXT UNIQUE,
                    company TEXT,
                    description TEXT,
                    evaluation_score REAL,
                    visited_at TEXT,
                    notified INTEGER DEFAULT 0
                )
            """)

    def is_visited(self, link):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT 1 FROM jobs WHERE link = ?", (link,))
            return cur.fetchone() is not None

    def save_job(self, job_data):
        """job_data: dict com as infos extraídas + evaluation"""
        eval_data = job_data.get("evaluation", {})

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO jobs (
                    id, title, link, company, description,
                    evaluation_score, visited_at, notified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data.get('link'),  # usa link como ID único
                job_data.get('title'),
                job_data.get('link'),
                job_data.get('company'),
                job_data.get('description'),
                eval_data.get('score'),
                datetime.utcnow().isoformat(),
                0  # ainda não notificou
            ))
            conn.commit()