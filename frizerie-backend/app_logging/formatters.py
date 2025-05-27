import json
import logging
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        # Add exception info if it exists
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        return json.dumps(log_data)

class RequestFormatter(logging.Formatter):
    """Format request log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the request log record."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        }
        
        # Add request-specific fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "process_time"):
            log_data["process_time"] = record.process_time
            
        return json.dumps(log_data)

class ErrorFormatter(logging.Formatter):
    """Format error log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the error log record."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add error-specific fields
        if record.exc_info:
            log_data["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        return json.dumps(log_data) 