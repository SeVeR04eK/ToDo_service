from app.domain.exceptions.base import DomainException


class RateLimitExceededError(DomainException):
    """Raised when a rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__("Rate limit exceeded")
