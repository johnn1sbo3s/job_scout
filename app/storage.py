import sqlite3
from datetime import datetime
from .logger import logger
import os
import json

class Storage:
    def __init__(self, db_path="data/jobs.db"):
        self.db_path = db_path

        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self._init_db()
        logger.info(f"Storage inicializado: {self.db_path}")

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        link TEXT UNIQUE,
                        subscription_link TEXT,
                        company TEXT,
                        description TEXT,
                        evaluation JSON,
                        evaluation_score REAL,
                        decision TEXT,
                        visited_at TEXT,
                        notified INTEGER DEFAULT 0
                    )
                """)
            logger.debug("Tabela 'jobs' verificada/criada com sucesso")
        except Exception:
            logger.exception("Erro ao inicializar banco de dados")
            raise

    def is_visited(self, link):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("SELECT 1 FROM jobs WHERE link = ?", (link,))
                result = cur.fetchone() is not None
                logger.debug(f"Vaga {'já visitada' if result else 'nova'}: {link}")
                return result
        except Exception:
            logger.exception(f"Erro ao verificar se vaga foi visitada: {link}")
            return False

    def save_job(self, job_data):
        eval_data = job_data.get("evaluation", {})

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO jobs (
                        id,
                        title,
                        link,
                        subscription_link,
                        company,
                        description,
                        evaluation,
                        evaluation_score,
                        decision,
                        visited_at,
                        notified
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data.get('link'),
                    job_data.get('title'),
                    job_data.get('link'),
                    job_data.get('subscription_link'),
                    job_data.get('company'),
                    job_data.get('description'),
                    json.dumps(eval_data, ensure_ascii=False),
                    eval_data.get('score'),
                    eval_data.get('decision'),
                    datetime.utcnow().isoformat(),
                    0
                ))
                conn.commit()

            logger.info(
                f"Vaga salva: {job_data.get('title')} "
                f"(score={eval_data.get('score')}, decision={eval_data.get('decision')})"
            )

        except Exception:
            logger.exception("Erro ao salvar vaga no banco")
            raise