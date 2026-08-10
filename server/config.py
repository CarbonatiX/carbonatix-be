from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore"
    )

    MONGODB_URI: str
    MONGODB_DB_NAME: str
    JWT_SECRET_KEY: str

    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")

    # Elice Sol (advisor + document interpret) / Helpy document vision.
    # Optional at process start so unit tests can load Settings; live routes
    # fail with 503 when these are missing at call time.
    ELICE_API_KEY: str = ""
    ELICE_BASE_URL: str = ""
    HELPY_BASE_URL: str = ""
    ELICE_MODEL: str = "gpt-5.6-sol"


settings = Settings()
