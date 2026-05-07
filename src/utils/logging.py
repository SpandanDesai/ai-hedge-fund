"""Structured logging and error handling system for AI Hedge Fund."""

import logging
import json
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path

from src.config import config


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class StructuredLogRecord:
    """Structured log record with standardized fields."""
    timestamp: str
    level: LogLevel
    logger: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Remove None values for cleaner output
        result = {k: v for k, v in result.items() if v is not None}
        return result


class StructuredLogger:
    """Structured logger that produces JSON-formatted logs."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
        self.correlation_id = None
        self.request_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for distributed tracing."""
        self.correlation_id = correlation_id
    
    def set_request_id(self, request_id: str):
        """Set request ID for request tracing."""
        self.request_id = request_id
    
    def _create_log_record(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None, 
                          error: Optional[Exception] = None) -> StructuredLogRecord:
        """Create a structured log record."""
        frame = sys._getframe(3)  # Skip internal frames
        
        error_type = None
        error_message = None
        stack_trace = None
        
        if error:
            error_type = error.__class__.__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
        
        return StructuredLogRecord(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            logger=self.name,
            message=message,
            module=frame.f_globals.get('__name__', ''),
            function=frame.f_code.co_name,
            line_number=frame.f_lineno,
            thread_id=logging.current_thread().ident,
            process_id=logging.current_process().ident,
            correlation_id=self.correlation_id,
            request_id=self.request_id,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            extra=extra
        )
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        record = self._create_log_record(LogLevel.DEBUG, message, kwargs)
        self.logger.debug(json.dumps(record.to_dict()))
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        record = self._create_log_record(LogLevel.INFO, message, kwargs)
        self.logger.info(json.dumps(record.to_dict()))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        record = self._create_log_record(LogLevel.WARNING, message, kwargs)
        self.logger.warning(json.dumps(record.to_dict()))
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with structured data and optional exception."""
        record = self._create_log_record(LogLevel.ERROR, message, kwargs, error)
        self.logger.error(json.dumps(record.to_dict()))
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message with structured data and optional exception."""
        record = self._create_log_record(LogLevel.CRITICAL, message, kwargs, error)
        self.logger.critical(json.dumps(record.to_dict()))


class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            # Parse the JSON message if it's already structured
            log_data = json.loads(record.getMessage())
        except (json.JSONDecodeError, TypeError):
            # Fallback to basic formatting
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line_number": record.lineno,
                "thread_id": record.thread,
                "process_id": record.process
            }
        
        return json.dumps(log_data)


def setup_logging():
    """Setup comprehensive logging configuration."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Clear existing handlers
    logging.getLogger().handlers.clear()
    
    # Create formatters
    json_formatter = JSONFormatter()
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        filename=logs_dir / "ai_hedge_fund.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(json_formatter)
    
    # Error file handler (errors only)
    error_handler = RotatingFileHandler(
        filename=logs_dir / "ai_hedge_fund_errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level.upper())
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    return root_logger


# Global logger instance
logger = StructuredLogger(__name__)


class ErrorHandler:
    """Comprehensive error handling with structured logging."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def handle_error(self, error: Exception, context: str = "", **kwargs):
        """Handle and log an error with context."""
        self.logger.error(
            f"Error in {context}: {str(error)}",
            error=error,
            **kwargs
        )
        
        # Additional error handling logic can be added here
        # For example: sending to error tracking service, retry logic, etc.
        
        return {
            "success": False,
            "error": error.__class__.__name__,
            "message": str(error),
            "context": context
        }
    
    def retry_on_failure(self, func, max_retries: int = 3, delay: float = 1.0, **kwargs):
        """Retry a function on failure with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as error:
                self.handle_error(
                    error,
                    context=f"retry attempt {attempt + 1}/{max_retries}",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    **kwargs
                )
                
                if attempt == max_retries - 1:
                    raise  # Re-raise on final attempt
                
                # Exponential backoff
                time.sleep(delay * (2 ** attempt))
        
        return None


# Global error handler instance
error_handler = ErrorHandler(logger)