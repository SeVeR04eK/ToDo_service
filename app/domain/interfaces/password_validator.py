from abc import ABC, abstractmethod


class PasswordValidator(ABC):
    """Interface for password validation."""

    @abstractmethod
    def validate(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        ...
