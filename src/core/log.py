"""Logging configuration."""
import logging
import logging.config
from pathlib import Path
from uuid import uuid4

from src.core.settings import settings


class AddErrorIdFilter(logging.Filter):
    """Filter to add unique error ID to error-level log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR and not hasattr(record, "error_id"):
            record.error_id = str(uuid4())
        return True


def configure_logging():
    """Configure logging with rotating file handler."""
    
    # Standard format for all logs
    default_fmt = {
        "format": "%(levelname)s %(asctime)s %(name)s:%(lineno)d — %(message)s"
    }

    # Ensure log file directory exists
    log_filepath = "logs/logs.log"
    Path(log_filepath).parent.mkdir(parents=True, exist_ok=True)

    logging_configuration = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"add_error_id": {"()": AddErrorIdFilter}},
        "formatters": {"default": default_fmt},
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": log_filepath,
                "maxBytes": 3 * 1024 * 1024,  # 3MB
                "backupCount": 10,
                "encoding": "utf-8",
                "filters": ["add_error_id"],
            },
        },
        "root": {
            "handlers": ["file"],
            "level": "INFO",
            "filters": ["add_error_id"],
        },
        "loggers": {
            "src": {
                "handlers": ["file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            # Suppress noisy third-party loggers
            "google": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "googleapiclient": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "google_auth_oauthlib": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "urllib3": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
            "requests": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            },
        }
    }

    logging.config.dictConfig(logging_configuration)
