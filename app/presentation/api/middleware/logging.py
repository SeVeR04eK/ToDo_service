import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with structured logging.
    
    This middleware logs:
    - HTTP method
    - Request path
    - Status code
    - Request duration in milliseconds
    
    All logs automatically include the correlation ID from the CorrelationIdMiddleware.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.perf_counter()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration in milliseconds
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Log the request completion
        logger = structlog.get_logger(__name__)

        log_method = logger.info if duration_ms < 1000 else logger.warning

        log_method(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        return response
