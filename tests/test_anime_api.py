import pytest
from fastapi.testclient import TestClient

from anime_analytics.config import Settings
from anime_analytics.main import create_app


def page_ids(response) -> list[int]:
    return [item["MAL_ID"] for item in response.json()["items"]]


# --- general -----------------------------


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Anime Analytics API",
        "version": "1.0.0",
        "environment": "development",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "dataset_loaded": True, "anime_count": 7}


def test_docs_and_openapi_are_served(client):
    assert client.get("/docs").status_code == 200

    schema = client.get("/openapi.json").json()
    assert set(schema["paths"]) == {
        "/",
        "/health",
        "/anime",
        "/anime/{mal_id}",
        "/analytics/overview",
        "/analytics/top-anime",
        "/analytics/genres",
        "/analytics/types",
        "/analytics/engagement",
        "/analytics/distribution/{metric}",
        "/analytics/pareto",
    }


def test_openapi_lists_supported_metrics_as_enum(client):
    schema = client.get("/openapi.json").json()
    parameters = schema["paths"]["/analytics/pareto"]["get"]["parameters"]
    metric = next(p for p in parameters if p["name"] == "metric")

    assert "Completed" in metric["schema"]["enum"]
    assert "Score" not in metric["schema"]["enum"]


# --- listing, filtering, pagination ----------------------------------------------


def test_list_anime_default_page(client):
    response = client.get("/anime")

    body = response.json()
    assert response.status_code == 200
    assert body["total"] == 7
    assert body["limit"] == 20 and body["offset"] == 0 and body["count"] == 7
    assert page_ids(response) == [1, 2, 3, 4, 5, 6, 7]


def test_list_anime_pagination(client):
    response = client.get("/anime", params={"limit": 3, "offset": 2})

    body = response.json()
    assert page_ids(response) == [3, 4, 5]
    assert (body["total"], body["count"], body["limit"], body["offset"]) == (7, 3, 3, 2)


def test_list_anime_offset_past_the_end_is_empty_not_an_error(client):
    response = client.get("/anime", params={"offset": 100})

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 7


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"anime_type": "tv"}, [1, 3, 5]),
        ({"genre": "action"}, [1, 2, 5]),
        ({"genre": "action", "anime_type": "TV"}, [1, 5]),
        ({"name": "force"}, [4]),
        ({"min_score": 7}, [1, 2, 5]),
        ({"max_score": 6}, [4, 7]),
        ({"anime_type": "Nothing"}, []),
        ({"sort_by": "Score", "order": "desc"}, [5, 1, 2, 4, 7, 3, 6]),
        ({"sort_by": "Name"}, [1, 2, 4, 5, 7, 3, 6]),
        ({"sort_by": "Members", "order": "asc"}, [6, 7, 5, 4, 3, 2, 1]),
    ],
)
def test_list_anime_filters_and_sorting(client, params, expected):
    response = client.get("/anime", params=params)

    assert response.status_code == 200
    assert page_ids(response) == expected
    assert response.json()["total"] == len(expected)


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": "ten"},
        {"offset": -1},
        {"sort_by": "Genres"},
        {"sort_by": "not_a_column"},
        {"order": "sideways"},
        {"min_score": 11},
        {"min_score": -1},
        {"min_score": 9, "max_score": 1},
    ],
)
def test_list_anime_rejects_invalid_parameters(client, params):
    response = client.get("/anime", params=params)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_anime_maximum_page_size_is_allowed(client):
    assert client.get("/anime", params={"limit": 100}).status_code == 200


# --- single record -----------------------------


def test_get_anime_by_id(client):
    response = client.get("/anime/1")

    assert response.status_code == 200
    body = response.json()
    assert body["MAL_ID"] == 1
    assert body["Name"] == "Alpha"
    assert body["Score"] == 8.5
    assert body["Genres"] == ["Action", "Comedy"]
    assert body["Type"] == "TV"
    assert body["Episodes"] == 12
    assert body["On-Hold"] == 50
    assert body["Plan to Watch"] == 300
    assert body["English name"] == "First Letter"


def test_get_anime_reports_missing_values_as_null(client):
    body = client.get("/anime/6").json()

    assert body["Score"] is None
    assert body["Type"] is None
    assert body["English name"] is None
    assert body["Genres"] == []


def test_record_and_list_item_have_the_same_shape(client):
    single = client.get("/anime/2").json()
    listed = client.get("/anime", params={"limit": 2}).json()["items"][1]

    assert single == listed


def test_get_anime_unknown_id_is_404(client):
    response = client.get("/anime/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Anime 999 not found"}


@pytest.mark.parametrize("bad_id", ["abc", "0", "-5", "1.5"])
def test_get_anime_invalid_id_is_422(client, bad_id):
    assert client.get(f"/anime/{bad_id}").status_code == 422


# --- dataset availability and startup -----------------------------


def test_app_loads_dataset_at_startup(tmp_path, raw_anime):
    path = tmp_path / "anime.csv"
    raw_anime.to_csv(path, index=False)
    app = create_app(Settings(_env_file=None, data_path=path))

    with TestClient(app) as client:
        assert client.get("/health").json()["anime_count"] == 7
        assert client.get("/anime/1").status_code == 200


def test_app_starts_without_dataset_and_reports_it(tmp_path):
    missing = tmp_path / "private" / "nope.csv"
    app = create_app(Settings(_env_file=None, data_path=missing))

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {
            "status": "degraded",
            "dataset_loaded": False,
            "anime_count": None,
        }

        for url in ("/anime", "/anime/1", "/analytics/overview", "/analytics/pareto"):
            response = client.get(url)
            assert response.status_code == 503
            assert "not available" in response.json()["detail"]
            assert "nope.csv" not in response.text  # no local paths leak
            assert str(tmp_path) not in response.text

        assert client.get("/").status_code == 200


def test_app_starts_with_invalid_dataset(tmp_path):
    path = tmp_path / "anime.csv"
    path.write_text("a,b\n1,2\n")
    app = create_app(Settings(_env_file=None, data_path=path))

    with TestClient(app) as client:
        assert client.get("/health").json()["dataset_loaded"] is False
        assert client.get("/anime").status_code == 503


def test_unknown_route_is_404(client):
    assert client.get("/nope").status_code == 404
