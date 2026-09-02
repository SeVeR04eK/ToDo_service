from app.domain.exceptions.base import DomainException

class SerializationError(DomainException):
    """Raised when serialization or deserialization fails."""
    pass