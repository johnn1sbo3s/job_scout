import logging
import sys
from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self, name=job_scout, log_dir="logs", level=logging.INFO):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.loger.addHandler(console_handler)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"run_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"Logger inicializado. Arquivo: {log_file}")

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def exception(self, message):
        self.logger.exception(message)

    def debug(self, message):
        self.logger.debug(message)

logger = Logger()