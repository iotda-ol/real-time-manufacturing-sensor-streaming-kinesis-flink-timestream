"""
Logger Module

Provides structured logging for the application.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json


class Logger:
    """
    Structured logger with support for JSON formatting and CloudWatch.
    
    Features:
    - Structured logging with context
    - JSON output for CloudWatch Logs Insights
    - Multiple log levels
    - Custom formatters
    """
    
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        json_format: bool = False,
        log_file: Optional[str] = None,
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_format: Use JSON formatting
            log_file: Optional file path for logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.json_format = json_format
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        if json_format:
            console_handler.setFormatter(JsonFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter(self.DEFAULT_FORMAT)
            )
        
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            
            if json_format:
                file_handler.setFormatter(JsonFormatter())
            else:
                file_handler.setFormatter(
                    logging.Formatter(self.DEFAULT_FORMAT)
                )
            
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """
        Internal logging method with context.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context to include
        """
        if kwargs:
            extra = {"context": kwargs}
            self.logger.log(level, message, extra=extra)
        else:
            self.logger.log(level, message)
    
    def get_logger(self) -> logging.Logger:
        """Get underlying logger instance."""
        return self.logger


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom context if present
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        return json.dumps(log_data)


def get_logger(
    name: str,
    level: str = "INFO",
    json_format: bool = False,
) -> Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        level: Log level
        json_format: Use JSON formatting
        
    Returns:
        Logger instance
    """
    return Logger(name, level, json_format)


if __name__ == "__main__":
    # Example usage
    
    # Standard logging
    logger = Logger("test-app", level="DEBUG")
    logger.info("Application started")
    logger.debug("Debug information", user_id=123, action="login")
    logger.warning("Warning message", threshold=0.8)
    logger.error("Error occurred", error_code=500)
    
    # JSON logging
    json_logger = Logger("test-app-json", level="INFO", json_format=True)
    json_logger.info("JSON formatted log", request_id="abc-123", duration_ms=150)
