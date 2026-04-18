from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    first_admin_username: str
    first_admin_password: str
    database_url: str
    secret_key: str
    access_token_expire_minutes: timedelta = timedelta(minutes = 15)
    refresh_token_expire_days: timedelta = timedelta(days = 7)
    algorithm: str = 'HS256'

    model_config = SettingsConfigDict(env_file = str(BASE_DIR / ".env"), env_file_encoding = "utf-8")

settings = Settings()
