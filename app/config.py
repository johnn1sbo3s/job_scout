import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()

        self.project_root = Path(__file__).resolve().parent.parent
        self.db_path = os.getenv("DB_PATH", "data/jobs.db")

        self.profile = self._load_yaml("profile.yaml")
        self.resume = self._load_text("resume.md")

        self.api_key = os.getenv("ROUTELLM_API_KEY") or os.getenv("ABACUS_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def _load_yaml(self, filename):
        path = self.project_root / filename
        if not path.exists():
            path = self.project_root / f"{filename}.example"

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}

        return {}

    def _load_text(self, filename):
        path = self.project_root / filename
        if not path.exists():
            path = self.project_root / f"{filename}.example"

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        return ""

    @property
    def min_score(self):
        return self.profile.get("min_score_to_notify", 70)

config = Config()