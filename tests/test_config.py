import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from anime_analytics import __version__
from anime_analytics.config import Settings, get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def clean_env(monkeypatch):
    """Remove real settings variables so defaults can be tested."""
    for name in ("APP_NAME", "APP_ENV", "DATA_PATH", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)


def test_defaults(clean_env):
    settings = Settings(_env_file=None)

    assert settings.app_name == "Anime Analytics API"
    assert settings.data_path == Path("data/anime.csv")
    assert settings.log_level == "INFO"


def test_environment_variables_override_defaults(monkeypatch):
    monkeypatch.setenv("DATA_PATH", "somewhere/else.csv")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("APP_ENV", "production")

    settings = Settings(_env_file=None)

    assert settings.data_path == Path("somewhere/else.csv")
    assert settings.log_level == "DEBUG"
    assert settings.app_env == "production"


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "LOUD")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_are_cached():
    assert get_settings() is get_settings()


def test_no_absolute_local_paths_in_default_configuration(clean_env):
    assert not Settings(_env_file=None).data_path.is_absolute()


def test_env_example_lists_every_setting():
    text = (PROJECT_ROOT / ".env.example").read_text()

    for variable in ("APP_NAME", "APP_ENV", "DATA_PATH", "LOG_LEVEL"):
        assert variable in text


def test_package_version_matches_pyproject():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert project["version"] == __version__
