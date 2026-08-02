"""Domain exceptions for the application.

These exceptions are raised by the service layer and caught by the router layer
to convert them into appropriate HTTP responses.
"""


class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass