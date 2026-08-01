from passlib.context import CryptContext

from app.domain.interfaces import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):

    def __init__(self):
        self.context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )

    def hash(self, password: str) -> str:
        return self.context.hash(password)

    def verify(
        self,
        plain: str,
        hashed: str,
    ) -> bool:
        return self.context.verify(
            plain,
            hashed,
        )