from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: timedelta = timedelta(minutes = 15)
    refresh_token_expire_days: timedelta = timedelta(days = 7)
    algorithm: str = 'HS256'

    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding = "utf-8")

settings = Settings()
