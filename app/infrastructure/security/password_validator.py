import re
from app.domain.interfaces import PasswordValidator


class CommonPasswordValidator(PasswordValidator):
    """Validates password strength and checks against common weak passwords."""

    # List of common weak passwords (can be extended)
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123", "monkey",
        "123456789", "letmein", "dragon", "111111", "baseball", "iloveyou",
        "trustno1", "sunshine", "master", "hello", "football", "jesus",
        "ninja", "mustang", "password1", "1234567", "welcome", "login",
        "princess", "solo", "admin", "123123", "shadow", "654321",
        "superman", "qazwsx", "michael", "123qwe", "password123",
        "qwerty123", "1q2w3e4r", "123abc", "test123", "admin123",
        "letmein123", "dragon123", "monkey123"
    }

    # Common patterns to reject (only at start or end)
    WEAK_PATTERNS = []

    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check minimum length
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"

        # Check against common passwords
        if password.lower() in self.COMMON_PASSWORDS:
            return False, "Password is too common. Please choose a stronger password"

        # Check for basic complexity (at least one letter and one digit)
        if not re.search(r"[a-zA-Z]", password):
            return False, "Password must contain at least one letter"

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        # Check for weak patterns
        password_lower = password.lower()
        for pattern in self.WEAK_PATTERNS:
            if re.search(pattern, password_lower):
                return False, "Password contains weak patterns. Please choose a stronger password"

        return True, ""
