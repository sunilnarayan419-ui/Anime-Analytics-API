"""Ranking and top-N retrieval."""

import pandas as pd

from anime_analytics.analytics.metrics import numeric_series, validate_positive_int

_IDENTIFIER_COLUMNS = ("MAL_ID", "Name", "Type")


def rank_top_n(
    data: pd.DataFrame,
    metric_column: str,
    n: int = 10,
    *,
    ascending: bool = False,
) -> pd.DataFrame:
    """Return the top ``n`` rows by a metric.

    Rows without a valid value for the metric are excluded. Ties are broken
    by the original row order, so the result is deterministic.

    Returns:
        DataFrame with ``rank`` (1-based), the identifier columns present in
        ``data`` (``MAL_ID``, ``Name``, ``Type``) and ``value``.

    Raises:
        AnalysisError: If ``n`` is not a positive integer or the column is
            unknown.
    """
    n = validate_positive_int(n, "n")
    # Work on a 0..len-1 index so duplicate index labels in ``data`` are harmless.
    table = data.reset_index(drop=True)
    values = numeric_series(table, metric_column).dropna()

    ordered = values.sort_values(ascending=ascending, kind="mergesort").head(n)

    identifiers = [column for column in _IDENTIFIER_COLUMNS if column in table.columns]
    result = table.loc[ordered.index, identifiers].copy()
    result.insert(0, "rank", range(1, len(ordered) + 1))
    result["value"] = ordered
    return result.reset_index(drop=True)
