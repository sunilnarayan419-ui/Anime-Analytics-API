import math
from typing import get_args

import numpy as np
import pandas as pd
import pytest

from anime_analytics.analytics.aggregation import (
    aggregate_by_category,
    aggregate_by_genre,
    aggregate_by_type,
)
from anime_analytics.analytics.descriptive import describe_metric
from anime_analytics.analytics.distribution import analyze_metric_distribution
from anime_analytics.analytics.engagement import (
    add_engagement_metrics,
    summarize_engagement_by_type,
)
from anime_analytics.analytics.metrics import (
    METRICS,
    CountMetricName,
    MetricName,
    get_metric,
    numeric_series,
    validate_positive_int,
)
from anime_analytics.analytics.ranking import rank_top_n
from anime_analytics.exceptions import AnalysisError
from anime_analytics.repositories.anime_repository import SORTABLE_COLUMNS
from anime_analytics.schemas.analytics import DistributionResponse
from anime_analytics.schemas.anime import SortField

# --- metric registry -----------------------------


def test_metric_literals_match_registry():
    assert set(get_args(MetricName)) == set(METRICS)
    additive = {name for name, info in METRICS.items() if info.kind == "count"}
    assert set(get_args(CountMetricName)) == additive


def test_sort_fields_match_repository():
    assert set(get_args(SortField)) == set(SORTABLE_COLUMNS)


def test_registry_kinds():
    assert get_metric("Members").kind == "count"
    assert get_metric("Score").kind == "score"
    assert get_metric("Popularity").kind == "rank"


def test_unsupported_metric_is_rejected():
    with pytest.raises(AnalysisError, match="Unsupported metric"):
        get_metric("Name")


def test_validate_positive_int():
    assert validate_positive_int(3, "n") == 3
    assert validate_positive_int(np.int64(2), "n") == 2
    for bad in (0, -1, 1.0, "1", True, None):
        with pytest.raises(AnalysisError):
            validate_positive_int(bad, "n")


def test_numeric_series_coerces_and_never_mutates():
    data = pd.DataFrame({"x": ["1", "Unknown", "2.5", None, "inf"]})
    before = data.copy(deep=True)

    result = numeric_series(data, "x")

    assert result.tolist()[0] == 1.0
    assert result.tolist()[2] == 2.5
    assert result.isna().tolist() == [False, True, False, True, True]
    pd.testing.assert_frame_equal(data, before)


def test_numeric_series_unknown_column():
    with pytest.raises(AnalysisError, match="Unknown metric column"):
        numeric_series(pd.DataFrame({"x": [1]}), "y")


# --- descriptive statistics -----------------------------


def test_descriptive_statistics(clean_anime):
    result = describe_metric(clean_anime, "Completed")

    assert result["count"] == 7
    assert result["missing"] == 0
    assert result["sum"] == 1600
    assert result["mean"] == pytest.approx(1600 / 7)
    assert result["median"] == 200
    assert result["minimum"] == 50
    assert result["maximum"] == 500
    assert result["q1"] == 75
    assert result["q3"] == 350
    assert result["std"] == pytest.approx(
        np.std([500, 400, 300, 200, 100, 50, 50], ddof=1)
    )


def test_descriptive_statistics_ignore_missing_values(clean_anime):
    result = describe_metric(clean_anime, "Score")

    assert result["count"] == 5
    assert result["missing"] == 2
    assert result["mean"] == pytest.approx((8.5 + 7 + 6 + 9 + 5) / 5)


def test_descriptive_single_value_has_nan_std():
    result = describe_metric(pd.DataFrame({"x": [4]}), "x")

    assert result["count"] == 1
    assert math.isnan(result["std"])


def test_descriptive_rejects_unknown_and_empty_columns():
    with pytest.raises(AnalysisError):
        describe_metric(pd.DataFrame({"x": [1]}), "Unknown")
    with pytest.raises(ValueError):  # AnalysisError is a ValueError
        describe_metric(pd.DataFrame({"x": ["a", None]}), "x")


# --- ranking -----------------------------


def test_top_n_descending(clean_anime):
    result = rank_top_n(clean_anime, "Members", 3)

    assert result.columns.tolist() == ["rank", "MAL_ID", "Name", "Type", "value"]
    assert result["rank"].tolist() == [1, 2, 3]
    assert result["Name"].tolist() == ["Alpha", "Beta", "Gamma"]
    assert result["value"].tolist() == [1000, 800, 600]


def test_top_n_ascending_breaks_ties_by_row_order(clean_anime):
    result = rank_top_n(clean_anime, "Members", 2, ascending=True)

    assert result["Name"].tolist() == ["Zeta", "Eta"]  # both have 100 members


def test_top_n_excludes_missing_values(clean_anime):
    result = rank_top_n(clean_anime, "Score", 10)

    assert result["Name"].tolist() == ["Epsilon", "Alpha", "Beta", "Delta Force", "Eta"]


def test_top_n_larger_than_data_returns_everything(clean_anime):
    assert len(rank_top_n(clean_anime, "Members", 100)) == 7


def test_top_n_works_without_identifier_columns():
    result = rank_top_n(pd.DataFrame({"x": [1, 3, 2]}), "x", 2)

    assert result.columns.tolist() == ["rank", "value"]
    assert result["value"].tolist() == [3, 2]


@pytest.mark.parametrize("n", [0, -1, 1.5, "2", True])
def test_top_n_rejects_invalid_n(clean_anime, n):
    with pytest.raises(AnalysisError):
        rank_top_n(clean_anime, "Members", n)


def test_top_n_rejects_unknown_metric(clean_anime):
    with pytest.raises(AnalysisError):
        rank_top_n(clean_anime, "Nope", 3)


# --- aggregation -----------------------------


def test_genre_aggregation_counts_each_anime_in_every_genre(clean_anime):
    result = aggregate_by_genre(clean_anime, "Completed")

    assert result.columns.tolist() == [
        "genre",
        "anime_count",
        "total",
        "mean",
        "median",
    ]
    assert result["genre"].tolist() == ["Action", "Comedy", "Drama"]
    assert result["total"].tolist() == [1000, 850, 600]
    assert result["anime_count"].tolist() == [3, 3, 3]
    # Full credit per genre: genre totals exceed the dataset total.
    assert result["total"].sum() > clean_anime["Completed"].sum()


def test_genre_aggregation_skips_missing_genres_and_missing_values(clean_anime):
    result = aggregate_by_genre(clean_anime, "Score", sort_by="mean")

    by_genre = result.set_index("genre")
    assert by_genre.loc["Action", "mean"] == pytest.approx((8.5 + 7 + 9) / 3)
    assert by_genre.loc["Comedy", "anime_count"] == 2  # Gamma has no score
    assert by_genre.loc["Drama", "mean"] == pytest.approx((6 + 9) / 2)
    assert result["genre"].tolist() == ["Action", "Drama", "Comedy"]
    assert "Unknown" not in result["genre"].tolist()  # Zeta has no genres


def test_genre_aggregation_handles_irregular_spacing():
    data = pd.DataFrame({"Genres": ["A,B", " A ,  C", None], "v": [1, 2, 4]})

    result = aggregate_by_genre(data, "v").set_index("genre")

    assert result["total"].to_dict() == {"A": 3, "B": 1, "C": 2}


def test_genre_aggregation_min_count_and_order(clean_anime):
    result = aggregate_by_genre(
        clean_anime, "Score", sort_by="anime_count", ascending=True, min_count=3
    )

    assert result["genre"].tolist() == ["Action"]


def test_genre_aggregation_validation(clean_anime):
    with pytest.raises(AnalysisError, match="sort_by"):
        aggregate_by_genre(clean_anime, "Completed", sort_by="bogus")
    with pytest.raises(AnalysisError, match="Unknown metric"):
        aggregate_by_genre(clean_anime, "Nope")
    with pytest.raises(AnalysisError, match="Genres"):
        aggregate_by_genre(clean_anime.drop(columns=["Genres"]), "Completed")
    all_missing = clean_anime.assign(Completed=pd.NA)
    with pytest.raises(AnalysisError, match="No valid numeric values"):
        aggregate_by_genre(all_missing, "Completed")


def test_type_aggregation_groups_missing_type_as_unknown(clean_anime):
    result = aggregate_by_type(clean_anime, "Completed")

    assert result["Type"].tolist() == ["TV", "Movie", "OVA", "Unknown"]
    assert result["total"].tolist() == [900, 400, 250, 50]
    assert result["anime_count"].tolist() == [3, 1, 2, 1]
    assert result.set_index("Type").loc["TV", "mean"] == pytest.approx(300)
    assert result.set_index("Type").loc["OVA", "median"] == pytest.approx(125)


def test_category_aggregation_validation(clean_anime):
    with pytest.raises(AnalysisError, match="Unknown category"):
        aggregate_by_category(clean_anime, "Nope", "Completed")


# --- distribution -----------------------------


def test_distribution_percentiles_are_values_not_levels(clean_anime):
    result = analyze_metric_distribution(clean_anime, "Completed", bins=4)

    # Regression: percentiles must hold metric values, not 25/50/75...
    assert result["percentiles"] == {
        "p25": 75.0,
        "p50": 200.0,
        "p75": 350.0,
        "p90": pytest.approx(440.0),
        "p95": pytest.approx(470.0),
        "p99": pytest.approx(494.0),
    }


def test_distribution_summary_and_histogram(clean_anime):
    result = analyze_metric_distribution(clean_anime, "Completed", bins=3)

    assert result["metric"] == "Completed"
    assert result["count"] == 7
    assert result["min"] == 50 and result["max"] == 500
    # Edges 50/200/350/500; bins are half-open except the last, so 200 is in bin 2.
    assert [b["count"] for b in result["histogram"]] == [3, 2, 2]
    assert sum(b["count"] for b in result["histogram"]) == 7
    assert result["histogram"][0]["lower"] == 50
    assert result["histogram"][-1]["upper"] == 500
    expected = pd.Series([500, 400, 300, 200, 100, 50, 50])
    assert result["skewness"] == pytest.approx(expected.skew())
    assert result["kurtosis"] == pytest.approx(expected.kurt())


def test_distribution_counts_missing_values(clean_anime):
    result = analyze_metric_distribution(clean_anime, "Score")

    assert result["count"] == 5
    assert result["missing"] == 2


def test_distribution_with_constant_values():
    result = analyze_metric_distribution(pd.DataFrame({"x": [2, 2, 2]}), "x", bins=4)

    assert sum(b["count"] for b in result["histogram"]) == 3
    assert result["std"] == 0


def test_distribution_of_few_values_has_nan_moments_and_serialises_to_null():
    result = analyze_metric_distribution(pd.DataFrame({"x": [1, 2]}), "x")

    assert math.isnan(result["skewness"]) and math.isnan(result["kurtosis"])
    payload = DistributionResponse.model_validate(result).model_dump()
    assert payload["skewness"] is None and payload["kurtosis"] is None


@pytest.mark.parametrize("bins", [0, -1, 101, 2.5, "3"])
def test_distribution_rejects_invalid_bins(clean_anime, bins):
    with pytest.raises(AnalysisError):
        analyze_metric_distribution(clean_anime, "Members", bins=bins)


def test_distribution_rejects_unknown_and_empty(clean_anime):
    with pytest.raises(AnalysisError):
        analyze_metric_distribution(clean_anime, "Nope")
    with pytest.raises(AnalysisError, match="No valid numeric values"):
        analyze_metric_distribution(pd.DataFrame({"x": [None, "a"]}), "x")


# --- engagement -----------------------------


def test_engagement_metrics_per_anime(clean_anime):
    result = add_engagement_metrics(clean_anime)
    alpha = result.loc[result["MAL_ID"] == 1].iloc[0]

    assert alpha["list_total"] == 1000
    assert alpha["completion_rate"] == pytest.approx(0.5)
    assert alpha["drop_rate"] == pytest.approx(0.05)
    assert alpha["favorite_rate"] == pytest.approx(0.1)
    assert "list_total" not in clean_anime.columns  # input untouched


def test_engagement_metrics_never_divide_by_zero_or_invent_values(clean_anime):
    data = clean_anime.copy()
    for column in ("Watching", "Completed", "On-Hold", "Dropped", "Plan to Watch"):
        data.loc[0, column] = 0
    data.loc[0, "Members"] = 0
    data.loc[1, "Dropped"] = pd.NA  # one missing status makes list_total unknown

    result = add_engagement_metrics(data)

    assert np.isnan(
        result.loc[0, ["completion_rate", "drop_rate", "favorite_rate"]]
    ).all()
    assert np.isnan(result.loc[1, "list_total"])
    assert np.isnan(result.loc[1, "completion_rate"])
    assert (
        not np.isinf(result[["completion_rate", "drop_rate", "favorite_rate"]])
        .any()
        .any()
    )


def test_engagement_by_type(clean_anime):
    result = summarize_engagement_by_type(clean_anime).set_index("Type")

    assert result.index.tolist() == ["TV", "Movie", "OVA", "Unknown"]
    tv = result.loc["TV"]
    assert tv["anime_count"] == 3
    assert tv["total_members"] == 1800
    assert tv["mean_completion_rate"] == pytest.approx(0.5)
    assert tv["mean_drop_rate"] == pytest.approx(0.05)
    assert tv["mean_favorite_rate"] == pytest.approx((0.1 + 10 / 600 + 0.25) / 3)


def test_engagement_min_members_filter(clean_anime):
    result = summarize_engagement_by_type(clean_anime, min_members=500)

    assert result["Type"].tolist() == ["TV", "Movie"]
    assert result.set_index("Type").loc["TV", "anime_count"] == 2


def test_engagement_validation(clean_anime):
    with pytest.raises(AnalysisError, match="min_members"):
        summarize_engagement_by_type(clean_anime, min_members=-1)
    with pytest.raises(AnalysisError, match="No anime match"):
        summarize_engagement_by_type(clean_anime, min_members=10**9)
    with pytest.raises(AnalysisError, match="Missing columns"):
        add_engagement_metrics(clean_anime.drop(columns=["Dropped"]))
