from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    MONGODB_URI: str
    MONGODB_DB_NAME: str
    JWT_SECRET_KEY: str

    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")


settings = Settings()
