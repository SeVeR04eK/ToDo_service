from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta

# Base directory of the project (used for .env file path)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    first_admin_username: str
    first_admin_password: str
    database_url: str
    secret_key: str
    # JWT token expiration times
    access_token_expire_minutes: timedelta = timedelta(minutes=15)
    refresh_token_expire_days: timedelta = timedelta(days=7)
    algorithm: str = 'HS256'
    debug: bool = False

    # Load settings from .env file in project root
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

# Global settings instance
settings = Settings()
