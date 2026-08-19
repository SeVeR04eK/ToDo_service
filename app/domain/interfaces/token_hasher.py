from abc import ABC, abstractmethod


class TokenHasher(ABC):
    """Interface for token hashing operations."""

    @abstractmethod
    def hash(self, token: str) -> str:
        """Hash a token for secure storage."""
        ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool:
        """
        Verify a token against its hash.
        NOTE: This method is not used in the application yet.
        """
        ...
