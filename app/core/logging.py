import logging
import sys
import structlog
from structlog.types import Processor

from app.core.config import settings


def setup_logging() -> None:
    """Configure logging and structlog for the application.
    
    This function sets up:
    - Standard Python logging with stdout output
    - Structlog for structured logging in JSON format
    - Processors for timestamp, log level, logger name, exceptions, and stack traces
    
    Raises:
        ValueError: If log_level configuration is invalid
        Exception: If structlog configuration fails
    """
    try:
        # Configure standard logging
        logging.basicConfig(
            level=settings.log_level,
            stream=sys.stdout,
            format="%(message)s",
        )
        
        # Configure structlog processors
        processors: list[Processor] = [
            # Add context variables from structlog.contextvars
            structlog.contextvars.merge_contextvars,
            
            # Add log level
            structlog.stdlib.add_log_level,
            
            # Add logger name
            structlog.stdlib.add_logger_name,
            
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            
            # Add stack info if requested
            structlog.processors.StackInfoRenderer(),
            
            # Format exceptions
            structlog.processors.format_exc_info,
            
            # Render to JSON
            structlog.processors.JSONRenderer(),
        ]
        
        # Configure structlog with standard library integration
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to configure logging: {e}") from e
