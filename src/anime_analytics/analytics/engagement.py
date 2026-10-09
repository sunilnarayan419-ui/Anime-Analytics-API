"""Audience engagement analysis.

Definitions (per anime):

* ``list_total``      = Watching + Completed + On-Hold + Dropped + Plan to Watch
* ``completion_rate`` = Completed / list_total
* ``drop_rate``       = Dropped / list_total
* ``favorite_rate``   = Favorites / Members

A rate is missing (NaN) whenever an input is missing or its denominator is
zero; it is never replaced by 0. These are user-list statistics from
MyAnimeList, not measurements of viewing or streaming.
"""

import pandas as pd

from anime_analytics.analytics.metrics import numeric_series
from anime_analytics.exceptions import AnalysisError

LIST_STATUS_COLUMNS = ("Watching", "Completed", "On-Hold", "Dropped", "Plan to Watch")
_REQUIRED = (*LIST_STATUS_COLUMNS, "Favorites", "Members", "Type")


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide element-wise, giving NaN (not inf) where the denominator is 0."""
    return numerator / denominator.where(denominator > 0)


def add_engagement_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``data`` with the engagement columns added."""
    missing = [column for column in _REQUIRED if column not in data.columns]
    if missing:
        raise AnalysisError(f"Missing columns for engagement analysis: {missing}")

    status = pd.concat(
        [numeric_series(data, column) for column in LIST_STATUS_COLUMNS], axis=1
    )
    list_total = status.sum(axis=1, min_count=len(LIST_STATUS_COLUMNS))

    result = data.copy()
    result["list_total"] = list_total
    result["completion_rate"] = _safe_ratio(status["Completed"], list_total)
    result["drop_rate"] = _safe_ratio(status["Dropped"], list_total)
    result["favorite_rate"] = _safe_ratio(
        numeric_series(data, "Favorites"), numeric_series(data, "Members")
    )
    return result


def summarize_engagement_by_type(
    data: pd.DataFrame,
    min_members: int = 0,
) -> pd.DataFrame:
    """Average engagement rates for each anime type.

    Rates are averaged per title (each anime counts once, regardless of
    audience size). Very small audiences give noisy rates, so ``min_members``
    can exclude titles with fewer members.

    Returns:
        DataFrame with ``Type``, ``anime_count`` (titles included),
        ``total_members`` and the mean of each rate over the titles where it
        is defined.

    Raises:
        AnalysisError: If ``min_members`` is negative or no title qualifies.
    """
    if min_members < 0:
        raise AnalysisError("min_members must be zero or greater")

    enriched = add_engagement_metrics(data)
    members = numeric_series(enriched, "Members")
    enriched = enriched.loc[members.fillna(-1) >= min_members].copy()
    enriched["Type"] = enriched["Type"].astype("string").fillna("Unknown")
    enriched["members_value"] = numeric_series(enriched, "Members")

    if enriched.empty:
        raise AnalysisError("No anime match the engagement filter")

    grouped = enriched.groupby("Type", sort=True).agg(
        anime_count=("MAL_ID", "count"),
        total_members=("members_value", "sum"),
        mean_completion_rate=("completion_rate", "mean"),
        mean_drop_rate=("drop_rate", "mean"),
        mean_favorite_rate=("favorite_rate", "mean"),
    )
    return grouped.sort_values("total_members", ascending=False).reset_index()
