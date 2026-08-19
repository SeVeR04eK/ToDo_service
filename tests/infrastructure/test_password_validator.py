"""Tests for PasswordValidator."""
import pytest
from app.infrastructure.security.password_validator import CommonPasswordValidator


@pytest.mark.unit
class TestPasswordValidator:
    """Test suite for PasswordValidator."""

    @pytest.fixture
    def validator(self):
        return CommonPasswordValidator(min_length=8)

    def test_strong_password(self, validator):
        """Test that a strong password passes validation."""
        is_valid, error = validator.validate("StrongPass123!")
        assert is_valid is True
        assert error == ""

    def test_short_password(self, validator):
        """Test that short password fails validation."""
        is_valid, error = validator.validate("Short1!")
        assert is_valid is False
        assert "at least 8 characters" in error

    def test_common_password(self, validator):
        """Test that common passwords are rejected."""
        common_passwords = ["password123", "qwerty123", "letmein123", "dragon123", "monkey123"]
        for password in common_passwords:
            is_valid, error = validator.validate(password)
            assert is_valid is False
            assert "too common" in error

    def test_only_lowercase(self, validator):
        """Test that passwords with only lowercase letters and digits are accepted if not common."""
        is_valid, error = validator.validate("lowercase1")
        assert is_valid is True
        assert error == ""

    def test_only_uppercase(self, validator):
        """Test that passwords with only uppercase letters and digits are accepted if not common."""
        is_valid, error = validator.validate("UPPERCASE1")
        assert is_valid is True
        assert error == ""

    def test_only_numbers(self, validator):
        """Test that passwords with only numbers are rejected."""
        is_valid, error = validator.validate("87654321")
        assert is_valid is False
        assert "at least one letter" in error

    def test_no_letters(self, validator):
        """Test that passwords without letters are rejected."""
        is_valid, error = validator.validate("98765432")
        assert is_valid is False
        assert "at least one letter" in error

    def test_no_digits(self, validator):
        """Test that passwords without digits are rejected."""
        is_valid, error = validator.validate("NoDigitsHere")
        assert is_valid is False
        assert "at least one digit" in error

    def test_valid_minimal_password(self, validator):
        """Test that minimal valid password passes."""
        is_valid, error = validator.validate("MyPassword123")
        assert is_valid is True
        assert error == ""

    def test_custom_min_length(self):
        """Test validator with custom minimum length."""
        validator = CommonPasswordValidator(min_length=12)
        is_valid, error = validator.validate("Short1!")
        assert is_valid is False
        assert "at least 12 characters" in error

    def test_case_insensitive_common_passwords(self, validator):
        """Test that common passwords are rejected regardless of case."""
        is_valid, error = validator.validate("PASSWORD123")
        assert is_valid is False
        assert "too common" in error

        is_valid, error = validator.validate("QWERTY123")
        assert is_valid is False
        assert "too common" in error
