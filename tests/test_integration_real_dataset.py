"""Smoke tests against the real MyAnimeList ``anime.csv``.

Skipped automatically when the file is not present (it is not distributed with
this repository; see ``data/README.md``). Set ``DATA_PATH`` to test a file
stored somewhere else.
"""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from anime_analytics.analytics.metrics import METRICS
from anime_analytics.analytics.pareto import calculate_pareto
from anime_analytics.config import Settings
from anime_analytics.main import create_app
from anime_analytics.repositories.anime_repository import AnimeRepository

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _dataset_path() -> Path:
    path = Path(os.environ.get("DATA_PATH", "data/anime.csv"))
    return path if path.is_absolute() else PROJECT_ROOT / path


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _dataset_path().is_file(), reason="anime.csv dataset not available"
    ),
]


@pytest.fixture(scope="module")
def real_repository() -> AnimeRepository:
    return AnimeRepository.from_csv(_dataset_path())


@pytest.fixture(scope="module")
def real_client(real_repository) -> TestClient:
    return TestClient(create_app(Settings(_env_file=None), repository=real_repository))


def test_dataset_loads_and_is_clean(real_repository):
    data = real_repository.data

    assert len(data) > 10_000
    assert data["MAL_ID"].is_unique
    assert real_repository.report.duplicate_ids_removed == 0
    assert data.loc[data["MAL_ID"] == 1, "Name"].item() == "Cowboy Bebop"


def test_known_record(real_client):
    body = real_client.get("/anime/1").json()

    assert body["Name"] == "Cowboy Bebop"
    assert body["Score"] == pytest.approx(8.78)
    assert "Action" in body["Genres"]
    assert body["Episodes"] == 26


@pytest.mark.parametrize(
    "metric", [name for name, info in METRICS.items() if info.kind == "count"]
)
def test_pareto_sums_to_one_for_every_count_metric(real_repository, metric):
    for groups in (1, 5, 10):
        result = calculate_pareto(real_repository.data, metric, groups)

        assert result.sum() == pytest.approx(1.0)
        assert len(result) == groups
        assert result.is_monotonic_decreasing


def test_pareto_endpoint_on_real_data(real_client):
    body = real_client.get(
        "/analytics/pareto", params={"metric": "Completed", "n": 10}
    ).json()

    assert body["observations"] > 10_000
    assert body["results"][-1]["cumulative_proportion"] == pytest.approx(1.0)
    assert body["results"][0]["proportion"] > body["results"][-1]["proportion"]


@pytest.mark.parametrize(
    "url",
    [
        "/health",
        "/anime?limit=100&sort_by=Score&order=desc",
        "/anime?genre=Action&anime_type=TV&min_score=8",
        "/analytics/overview",
        "/analytics/top-anime?metric=Favorites&limit=5",
        "/analytics/top-anime?metric=Popularity&limit=5",
        "/analytics/genres?metric=Members",
        "/analytics/genres?metric=Score&min_anime=50",
        "/analytics/types?metric=Completed",
        "/analytics/engagement?min_members=1000",
        "/analytics/distribution/Members?bins=20",
        "/analytics/distribution/Score",
    ],
)
def test_endpoints_respond_on_real_data(real_client, url):
    response = real_client.get(url)

    assert response.status_code == 200
    assert "NaN" not in response.text


def test_rank_placeholders_do_not_top_the_popularity_ranking(real_client):
    items = real_client.get(
        "/analytics/top-anime", params={"metric": "Popularity", "limit": 3}
    ).json()["items"]

    assert [i["value"] for i in items] == [1.0, 2.0, 3.0]
