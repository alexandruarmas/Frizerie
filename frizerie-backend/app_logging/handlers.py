import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
import json
from datetime import datetime
from pathlib import Path

from .formatters import JSONFormatter, RequestFormatter, ErrorFormatter

class FileHandler(RotatingFileHandler):
    """Custom file handler with JSON formatting."""
    
    def __init__(
        self,
        filename: str,
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        formatter: Optional[logging.Formatter] = None
    ):
        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        self.setFormatter(formatter or JSONFormatter())

class ConsoleHandler(logging.StreamHandler):
    """Custom console handler with JSON formatting."""
    
    def __init__(self, formatter: Optional[logging.Formatter] = None):
        super().__init__()
        self.setFormatter(formatter or JSONFormatter())

class DatabaseHandler(logging.Handler):
    """Custom database handler for storing logs in the database."""
    
    def __init__(self, db_session, formatter: Optional[logging.Formatter] = None):
        super().__init__()
        self.db_session = db_session
        self.setFormatter(formatter or JSONFormatter())
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record to the database."""
        try:
            # Format the record
            msg = self.format(record)
            
            # Create log entry in database
            # Note: You'll need to implement the actual database model and insertion
            # log_entry = LogEntry(
            #     level=record.levelname,
            #     message=msg,
            #     timestamp=datetime.utcnow()
            # )
            # self.db_session.add(log_entry)
            # self.db_session.commit()
            
        except Exception:
            self.handleError(record)

class RequestHandler(FileHandler):
    """Handler specifically for request/response logging."""
    
    def __init__(
        self,
        filename: str = "logs/requests.log",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        encoding: str = 'utf-8'
    ):
        super().__init__(
            filename=filename,
            max_bytes=max_bytes,
            backup_count=backup_count,
            formatter=RequestFormatter()
        )

class ErrorHandler(FileHandler):
    """Handler specifically for error logging."""
    
    def __init__(
        self,
        filename: str = "logs/errors.log",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        encoding: str = 'utf-8'
    ):
        super().__init__(
            filename=filename,
            max_bytes=max_bytes,
            backup_count=backup_count,
            formatter=ErrorFormatter()
        ) 