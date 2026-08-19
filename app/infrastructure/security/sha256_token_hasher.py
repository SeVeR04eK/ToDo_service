import hashlib
from app.domain.interfaces import TokenHasher


class SHA256TokenHasher(TokenHasher):
    """SHA-256 based token hasher for secure token storage."""

    def hash(self, token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode()).hexdigest()

    def verify(self, plain: str, hashed: str) -> bool:
        """
        Verify a token against its hash.
        NOTE: This method is not used in the application yet.
        """
        return self.hash(plain) == hashed
