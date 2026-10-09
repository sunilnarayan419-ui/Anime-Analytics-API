import pytest


def names(response) -> list[str]:
    return [item["name"] for item in response.json()["items"]]


# --- overview -----------------------------


def test_overview(client):
    response = client.get("/analytics/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["total_anime"] == 7
    assert body["type_counts"] == {"TV": 3, "OVA": 2, "Movie": 1, "Unknown": 1}
    assert body["genre_count"] == 3
    assert body["data_quality"] == {
        "rows_raw": 7,
        "rows_clean": 7,
        "invalid_id_rows_removed": 0,
        "duplicate_ids_removed": 0,
        "invalid_values_set_missing": {},
    }


def test_overview_metric_summaries(client):
    metrics = client.get("/analytics/overview").json()["metrics"]

    assert metrics["Members"]["count"] == 7
    assert metrics["Members"]["sum"] == 3200
    assert metrics["Members"]["median"] == 400
    assert metrics["Score"]["count"] == 5
    assert metrics["Score"]["missing"] == 2
    assert metrics["Score"]["sum"] is None  # a sum of average scores is meaningless
    assert metrics["Episodes"]["missing"] == 1
    assert "Popularity" not in metrics  # a rank has no meaningful summary here


# --- top anime -----------------------------


def test_top_anime_defaults_to_members_descending(client):
    response = client.get("/analytics/top-anime")

    body = response.json()
    assert response.status_code == 200
    assert (body["metric"], body["order"], body["limit"], body["count"]) == (
        "Members",
        "desc",
        10,
        7,
    )
    assert names(response)[:3] == ["Alpha", "Beta", "Gamma"]
    assert body["items"][0] == {
        "rank": 1,
        "mal_id": 1,
        "name": "Alpha",
        "type": "TV",
        "value": 1000.0,
    }


def test_top_anime_limit_and_missing_values(client):
    response = client.get(
        "/analytics/top-anime", params={"metric": "Score", "limit": 2}
    )

    assert names(response) == ["Epsilon", "Alpha"]


def test_top_anime_rank_metrics_default_to_best_first(client):
    default = client.get("/analytics/top-anime", params={"metric": "Popularity"})
    reverse = client.get(
        "/analytics/top-anime", params={"metric": "Popularity", "order": "desc"}
    )

    assert default.json()["order"] == "asc"
    assert names(default)[0] == "Alpha"  # popularity rank 1
    assert names(reverse)[0] == "Eta"


def test_top_anime_missing_type_is_null(client):
    items = client.get("/analytics/top-anime", params={"limit": 100}).json()["items"]

    assert next(i for i in items if i["name"] == "Zeta")["type"] is None


@pytest.mark.parametrize(
    "params",
    [
        {"metric": "Name"},
        {"metric": "Genres"},
        {"metric": "nope"},
        {"limit": 0},
        {"limit": 101},
        {"order": "up"},
    ],
)
def test_top_anime_rejects_invalid_parameters(client, params):
    assert client.get("/analytics/top-anime", params=params).status_code == 422


# --- genres and types -----------------------------


def test_genres_default(client):
    response = client.get("/analytics/genres")

    body = response.json()
    assert response.status_code == 200
    assert (body["metric"], body["group_by"], body["sort_by"]) == (
        "Members",
        "genre",
        "total",
    )
    assert [(i["name"], i["total"], i["anime_count"]) for i in body["items"]] == [
        ("Action", 2000, 3),
        ("Comedy", 1700, 3),
        ("Drama", 1200, 3),
    ]


def test_genres_for_a_rating_metric_use_means_and_hide_totals(client):
    response = client.get("/analytics/genres", params={"metric": "Score"})

    body = response.json()
    assert body["sort_by"] == "mean"
    assert names(response) == ["Action", "Drama", "Comedy"]
    assert all(item["total"] is None for item in body["items"])
    assert body["items"][0]["mean"] == pytest.approx((8.5 + 7 + 9) / 3)


def test_genres_sorting_filtering_and_limit(client):
    ascending = client.get("/analytics/genres", params={"order": "asc"})
    assert names(ascending) == ["Drama", "Comedy", "Action"]

    by_count = client.get(
        "/analytics/genres", params={"metric": "Score", "min_anime": 3}
    )
    assert names(by_count) == ["Action"]

    limited = client.get("/analytics/genres", params={"limit": 1})
    assert names(limited) == ["Action"] and limited.json()["count"] == 1


def test_genres_total_sort_is_rejected_for_rating_metric(client):
    response = client.get(
        "/analytics/genres", params={"metric": "Score", "sort_by": "total"}
    )

    assert response.status_code == 400
    assert "only available for additive count metrics" in response.json()["detail"]


@pytest.mark.parametrize(
    "params",
    [{"metric": "Genres"}, {"sort_by": "name"}, {"min_anime": 0}, {"limit": 201}],
)
def test_genres_reject_invalid_parameters(client, params):
    assert client.get("/analytics/genres", params=params).status_code == 422


def test_genres_filter_that_removes_everything_returns_an_empty_list(client):
    response = client.get("/analytics/genres", params={"min_anime": 4})

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["count"] == 0


def test_types_comparison(client):
    response = client.get("/analytics/types")

    body = response.json()
    assert response.status_code == 200
    assert body["group_by"] == "type"
    assert [(i["name"], i["total"]) for i in body["items"]] == [
        ("TV", 1800),
        ("Movie", 800),
        ("OVA", 500),
        ("Unknown", 100),
    ]


def test_types_for_rating_metric(client):
    body = client.get("/analytics/types", params={"metric": "Score"}).json()

    assert body["sort_by"] == "mean"
    assert body["items"][0]["name"] == "TV"
    assert body["items"][0]["mean"] == pytest.approx((8.5 + 9) / 2)


# --- engagement -----------------------------


def test_engagement(client):
    response = client.get("/analytics/engagement")

    body = response.json()
    assert response.status_code == 200
    assert body["min_members"] == 0
    tv = body["items"][0]
    assert tv["type"] == "TV"
    assert tv["anime_count"] == 3
    assert tv["total_members"] == 1800
    assert tv["mean_completion_rate"] == pytest.approx(0.5)
    assert tv["mean_drop_rate"] == pytest.approx(0.05)


def test_engagement_min_members(client):
    body = client.get("/analytics/engagement", params={"min_members": 500}).json()

    assert [i["type"] for i in body["items"]] == ["TV", "Movie"]


def test_engagement_validation(client):
    assert (
        client.get("/analytics/engagement", params={"min_members": -1}).status_code
        == 422
    )
    too_high = client.get("/analytics/engagement", params={"min_members": 10**7})
    assert too_high.status_code == 400
    assert "No anime match" in too_high.json()["detail"]


# --- distribution -----------------------------


def test_distribution(client):
    response = client.get("/analytics/distribution/Members", params={"bins": 5})

    body = response.json()
    assert response.status_code == 200
    assert body["metric"] == "Members"
    assert body["count"] == 7 and body["missing"] == 0
    assert body["min"] == 100 and body["max"] == 1000
    assert body["median"] == 400
    assert body["percentiles"]["p50"] == 400
    assert len(body["histogram"]) == 5
    assert sum(b["count"] for b in body["histogram"]) == 7
    assert set(body["percentiles"]) == {"p25", "p50", "p75", "p90", "p95", "p99"}


def test_distribution_default_bins_and_missing_values(client):
    body = client.get("/analytics/distribution/Score").json()

    assert len(body["histogram"]) == 10
    assert body["count"] == 5 and body["missing"] == 2


def test_distribution_handles_metric_names_with_spaces_and_hyphens(client):
    assert client.get("/analytics/distribution/Plan%20to%20Watch").status_code == 200
    assert client.get("/analytics/distribution/On-Hold").status_code == 200
    # Valid metric name, but the small sample has no Score-10 column.
    assert client.get("/analytics/distribution/Score-10").status_code == 400


@pytest.mark.parametrize(
    "url",
    [
        "/analytics/distribution/Name",
        "/analytics/distribution/nope",
        "/analytics/distribution/Members?bins=0",
        "/analytics/distribution/Members?bins=101",
        "/analytics/distribution/Members?bins=abc",
    ],
)
def test_distribution_rejects_invalid_requests(client, url):
    assert client.get(url).status_code == 422


# --- pareto -----------------------------


def test_pareto(client):
    response = client.get("/analytics/pareto", params={"metric": "Completed", "n": 5})

    body = response.json()
    assert response.status_code == 200
    assert (body["metric"], body["groups"]) == ("Completed", 5)
    assert body["observations"] == 7 and body["excluded_missing"] == 0
    assert body["total"] == 1600
    assert [r["group"] for r in body["results"]] == [f"Group {i}" for i in range(1, 6)]
    proportions = [r["proportion"] for r in body["results"]]
    assert proportions == pytest.approx(
        [900 / 1600, 300 / 1600, 200 / 1600, 100 / 1600, 100 / 1600]
    )
    assert sum(proportions) == pytest.approx(1.0)
    assert body["results"][-1]["cumulative_proportion"] == pytest.approx(1.0)
    assert body["results"][0]["cumulative_proportion"] == pytest.approx(900 / 1600)


def test_pareto_reports_excluded_missing_values(client):
    body = client.get("/analytics/pareto", params={"metric": "Episodes", "n": 2}).json()

    assert body["observations"] == 6
    assert body["excluded_missing"] == 1
    assert body["total"] == 43


def test_pareto_more_groups_than_observations_is_400(client):
    response = client.get("/analytics/pareto", params={"n": 8})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Cannot form 8 groups from 7 valid observations"
    }


def test_pareto_default_group_count_needs_enough_data(client):
    # The default is 10 groups; the sample dataset only has 7 anime.
    assert client.get("/analytics/pareto").status_code == 400


@pytest.mark.parametrize(
    "params",
    [
        {"metric": "Score"},  # an average, not additive
        {"metric": "Popularity"},  # a rank, not additive
        {"metric": "Name"},
        {"metric": "nope"},
        {"n": 0},
        {"n": -2},
        {"n": 101},
        {"n": "x"},
        {"n": 2.5},
    ],
)
def test_pareto_rejects_invalid_parameters(client, params):
    assert client.get("/analytics/pareto", params={"n": 3, **params}).status_code == 422


# --- response consistency -----------------------------


def test_error_bodies_always_have_detail(client):
    for url in (
        "/anime/999",
        "/analytics/pareto?n=50",
        "/analytics/pareto?n=0",
        "/anime?limit=0",
    ):
        response = client.get(url)
        assert response.status_code >= 400
        assert "detail" in response.json()


def test_responses_contain_no_nan_or_infinity(client):
    for url in (
        "/analytics/overview",
        "/analytics/genres?metric=Score",
        "/analytics/engagement",
        "/analytics/distribution/Score",
        "/anime?limit=100",
    ):
        text = client.get(url).text
        assert "NaN" not in text and "Infinity" not in text, url


def test_analytics_endpoints_do_not_change_the_dataset(client, repository):
    before = repository.data.copy(deep=True)

    for url in (
        "/analytics/overview",
        "/analytics/top-anime",
        "/analytics/genres",
        "/analytics/types",
        "/analytics/engagement",
        "/analytics/distribution/Members",
        "/analytics/pareto?n=3",
    ):
        assert client.get(url).status_code == 200

    import pandas as pd

    pd.testing.assert_frame_equal(repository.data, before)
