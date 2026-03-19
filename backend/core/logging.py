"""Logging configuration."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)


def setup_logging(service_name: str = "job-automation", log_level: str = "INFO"):
    """Setup logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_handler.setFormatter(logging.Formatter(console_format))
    root_logger.addHandler(console_handler)
    
    # File handler (JSON for ingestion)
    file_handler = RotatingFileHandler(
        log_dir / f"{service_name}.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Error file handler (only errors)
    error_handler = RotatingFileHandler(
        log_dir / f"{service_name}_error.log",
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # Set third-party log levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("temporalio").setLevel(logging.WARNING)
    
    return root_logger


class LoggerMixin:
    """Mixin to add logger to classes."""
    
    @property
    def logger(self):
        """Get class-specific logger."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger