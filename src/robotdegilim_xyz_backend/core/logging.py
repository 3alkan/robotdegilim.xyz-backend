import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from robotdegilim_xyz_backend.core.config import get_settings

class JsonFormatter(logging.Formatter):
    """Formats log records as JSON for cloud observability."""
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)

def setup_logging() -> None:
    """Configures the root logger for the application/worker."""
    settings = get_settings()
    
    # Parse log level (default to INFO if invalid)
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Determine formatter
    if settings.LOG_JSON:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 1. Console Handler (Always enabled, good for Fly.io and Local)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Size-Rotating File Handler (Only enabled if LOG_TO_FILE=True)
    if settings.LOG_TO_FILE:
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Max 10MB per file, keep 5 backups (Total max 50MB)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
