from pathlib import Path
from pydantic import field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta

# Base directory of the project (used for .env file path)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.
    
    This class uses Pydantic Settings to load configuration from:
    1. Environment variables (highest priority)
    2. .env file in project root
    3. Default values (lowest priority)
    """

    # Database Configuration
    database_url: str
    
    # Security
    secret_key: SecretStr  # SecretStr prevents accidental logging of sensitive data
    
    # Admin User (for initial seeding)
    first_admin_username: str
    first_admin_password: SecretStr
    
    # JWT Token Configuration
    access_token_expire_minutes: timedelta = timedelta(minutes=15)
    refresh_token_expire_days: timedelta = timedelta(days=7)
    algorithm: str = "HS256"
    
    # Application Settings
    debug: bool = False

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        """Validate that secret key is not empty or too short."""
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security")
        return v

    @field_validator("first_admin_password")
    @classmethod
    def validate_admin_password(cls, v: SecretStr) -> SecretStr:
        """Validate that admin password meets minimum security requirements."""
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("FIRST_ADMIN_PASSWORD must be at least 8 characters long")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate that database URL is properly formatted."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://")):
            raise ValueError("DATABASE_URL must start with postgresql://, postgresql+asyncpg://, or sqlite://")
        return v

    # Load settings from .env file in project root
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow both uppercase and lowercase env var names
        extra="ignore"  # Ignore extra environment variables
    )


# Global settings instance
settings = Settings()
