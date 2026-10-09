"""Genre-level and category-level aggregation."""

import pandas as pd

from anime_analytics.analytics.metrics import numeric_series
from anime_analytics.exceptions import AnalysisError

SORT_COLUMNS = ("anime_count", "total", "mean", "median")
_OUTPUT_COLUMNS = ["anime_count", "total", "mean", "median"]


def _validate_sort(sort_by: str) -> None:
    if sort_by not in SORT_COLUMNS:
        raise AnalysisError(f"sort_by must be one of {list(SORT_COLUMNS)}")


def _summarise(
    frame: pd.DataFrame,
    key: str,
    *,
    sort_by: str,
    ascending: bool,
    min_count: int,
) -> pd.DataFrame:
    """Group ``frame`` (columns ``key`` and ``value``) and summarise ``value``."""
    grouped = frame.groupby(key, sort=False)["value"].agg(
        anime_count="count", total="sum", mean="mean", median="median"
    )
    grouped = grouped[grouped["anime_count"] >= min_count]
    grouped = grouped.reset_index().sort_values(
        [sort_by, key],
        ascending=[ascending, True],
        kind="mergesort",
    )
    result: pd.DataFrame = grouped[[key, *_OUTPUT_COLUMNS]].reset_index(drop=True)
    return result


def aggregate_by_category(
    data: pd.DataFrame,
    category_column: str,
    metric_column: str,
    *,
    missing_label: str = "Unknown",
    sort_by: str = "total",
    ascending: bool = False,
    min_count: int = 1,
) -> pd.DataFrame:
    """Summarise a metric for each value of a single-valued category column.

    Rows with a missing category are grouped under ``missing_label`` rather
    than dropped. Rows with a missing metric value are excluded.

    Returns:
        DataFrame with the category column plus ``anime_count`` (rows with a
        valid metric), ``total``, ``mean`` and ``median``.

    Raises:
        AnalysisError: For unknown columns, an invalid ``sort_by`` or when no
            valid metric values exist.
    """
    _validate_sort(sort_by)
    if category_column not in data.columns:
        raise AnalysisError(f"Unknown category column: {category_column}")

    values = numeric_series(data, metric_column)
    frame = pd.DataFrame(
        {
            category_column: data[category_column]
            .astype("string")
            .fillna(missing_label),
            "value": values,
        }
    ).dropna(subset=["value"])

    if frame.empty:
        raise AnalysisError(f"No valid numeric values for {metric_column}")

    return _summarise(
        frame,
        category_column,
        sort_by=sort_by,
        ascending=ascending,
        min_count=min_count,
    )


def aggregate_by_type(
    data: pd.DataFrame,
    metric_column: str,
    *,
    sort_by: str = "total",
    ascending: bool = False,
    min_count: int = 1,
) -> pd.DataFrame:
    """Compare anime formats (TV, Movie, OVA, ...) on a metric."""
    return aggregate_by_category(
        data,
        "Type",
        metric_column,
        sort_by=sort_by,
        ascending=ascending,
        min_count=min_count,
    )


def aggregate_by_genre(
    data: pd.DataFrame,
    metric_column: str,
    *,
    sort_by: str = "total",
    ascending: bool = False,
    min_count: int = 1,
) -> pd.DataFrame:
    """Summarise a metric for each genre.

    ``Genres`` holds a comma-separated list. Each anime is counted **in full**
    for every genre it lists, so one title with three genres appears in three
    rows and genre totals add up to more than the dataset total. Titles with
    no genre information are left out.

    Returns:
        DataFrame with ``genre``, ``anime_count``, ``total``, ``mean`` and
        ``median``.

    Raises:
        AnalysisError: For unknown columns, an invalid ``sort_by`` or when no
            valid metric values exist.
    """
    _validate_sort(sort_by)
    if "Genres" not in data.columns:
        raise AnalysisError("Genres column not found in data")

    values = numeric_series(data, metric_column)
    frame = pd.DataFrame(
        {
            "genre": data["Genres"].astype("string").str.split(","),
            "value": values,
        }
    ).dropna(subset=["value"])
    frame = frame.explode("genre")
    frame["genre"] = frame["genre"].astype("string").str.strip()
    frame = frame[frame["genre"].fillna("").str.len() > 0]

    if frame.empty:
        raise AnalysisError(f"No valid numeric values for {metric_column}")

    return _summarise(
        frame,
        "genre",
        sort_by=sort_by,
        ascending=ascending,
        min_count=min_count,
    )
