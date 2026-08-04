import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add a unique correlation ID to each request.
    
    This middleware generates a unique UUID for each incoming request and binds it
    to structlog contextvars, ensuring all logs generated during that request
    automatically include the request_id field.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate a unique correlation ID for this request
        request_id = str(uuid.uuid4())
        
        # Bind the request_id to structlog contextvars
        # This will automatically include request_id in all logs during this request
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Store the request_id in the request state for potential use in endpoints
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
        finally:
            # Clear the contextvars after the request is complete
            structlog.contextvars.unbind_contextvars("request_id")
        
        return response
