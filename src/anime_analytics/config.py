"""Application configuration.

Settings are read from environment variables (and an optional ``.env`` file).
See ``.env.example`` for the supported variables.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    """Runtime settings for the API."""

    app_name: str = "Anime Analytics API"
    app_env: str = "development"
    # Relative paths are resolved against the working directory the server is
    # started from (normally the project root).
    data_path: Path = Path("data/anime.csv")
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        level = value.upper()
        if level not in _LOG_LEVELS:
            raise ValueError(f"log_level must be one of {sorted(_LOG_LEVELS)}")
        return level


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings, created on first use."""
    return Settings()
