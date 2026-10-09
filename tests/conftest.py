"""Shared fixtures.

``raw_anime`` mimics the real CSV (everything is text and missing values are
the literal string ``"Unknown"``). The numbers are chosen so expected results
can be computed by hand:

    id  name         score  genres          type     members  completed
    1   Alpha        8.5    Action, Comedy  TV       1000     500
    2   Beta         7.0    Action          Movie    800      400
    3   Gamma        -      Comedy, Drama   TV       600      300
    4   Delta Force  6.0    Drama           OVA      400      200
    5   Epsilon      9.0    Action, Drama   TV       200      100
    6   Zeta         -      -               -        100      50
    7   Eta          5.0    Comedy          OVA      100      50

Zeta and Eta tie on Members and on Completed.
"""

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from anime_analytics.analytics.preprocessing import preprocess_anime
from anime_analytics.config import Settings
from anime_analytics.main import create_app
from anime_analytics.repositories.anime_repository import AnimeRepository

COLUMNS = [
    "MAL_ID",
    "Name",
    "Score",
    "Genres",
    "English name",
    "Type",
    "Episodes",
    "Popularity",
    "Members",
    "Favorites",
    "Watching",
    "Completed",
    "On-Hold",
    "Dropped",
    "Plan to Watch",
]

ROWS = [
    ("1", "Alpha", "8.50", "Action, Comedy", "First Letter", "TV", "12", "1",
     "1000", "100", "100", "500", "50", "50", "300"),
    ("2", "Beta", "7.00", "Action", "Second Letter", "Movie", "1", "2",
     "800", "40", "0", "400", "0", "40", "360"),
    ("3", "Gamma", "Unknown", "Comedy, Drama", "Unknown", "TV", "Unknown", "3",
     "600", "10", "60", "300", "30", "30", "180"),
    ("4", "Delta Force", "6.00", "Drama", "Unknown", "OVA", "2", "4",
     "400", "5", "40", "200", "20", "20", "120"),
    ("5", "Epsilon", "9.00", "Action, Drama", "Fifth Letter", "TV", "24", "5",
     "200", "50", "20", "100", "10", "10", "60"),
    ("6", "Zeta", "Unknown", "Unknown", "Unknown", "Unknown", "1", "6",
     "100", "0", "10", "50", "5", "5", "30"),
    ("7", "Eta", "5.00", "Comedy", "Unknown", "OVA", "3", "7",
     "100", "1", "10", "50", "5", "5", "30"),
]  # fmt: skip


@pytest.fixture
def raw_anime() -> pd.DataFrame:
    """A fresh raw (uncleaned) table; safe for tests to modify."""
    return pd.DataFrame(ROWS, columns=COLUMNS)


@pytest.fixture
def clean_anime(raw_anime: pd.DataFrame) -> pd.DataFrame:
    return preprocess_anime(raw_anime).data


@pytest.fixture
def repository(raw_anime: pd.DataFrame) -> AnimeRepository:
    return AnimeRepository.from_dataframe(raw_anime)


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None)


@pytest.fixture
def client(settings: Settings, repository: AnimeRepository) -> TestClient:
    return TestClient(create_app(settings=settings, repository=repository))
