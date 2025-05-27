import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_path = Path("logs")
log_path.mkdir(parents=True, exist_ok=True)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            "logs/app.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    ]
)

# Export commonly used functions and classes
from .formatters import JSONFormatter, RequestFormatter, ErrorFormatter
from .handlers import FileHandler, ConsoleHandler, DatabaseHandler
from .middleware import LoggingMiddleware

__all__ = [
    'JSONFormatter',
    'RequestFormatter',
    'ErrorFormatter',
    'FileHandler',
    'ConsoleHandler',
    'DatabaseHandler',
    'LoggingMiddleware'
] 