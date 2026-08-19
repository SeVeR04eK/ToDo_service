from app.infrastructure.security.sha256_token_hasher import SHA256TokenHasher
from app.domain.interfaces import TokenHasher


def get_token_hasher() -> TokenHasher:
    return SHA256TokenHasher()
