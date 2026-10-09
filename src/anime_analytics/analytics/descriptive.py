"""Descriptive statistics for a numeric column."""

import pandas as pd

from anime_analytics.analytics.metrics import numeric_series
from anime_analytics.exceptions import AnalysisError


def describe_metric(data: pd.DataFrame, metric_column: str) -> dict[str, float | int]:
    """Summarise the valid (non-missing, numeric) values of a column.

    Returns:
        ``count`` of valid values, ``missing`` (rows without a valid value),
        ``mean``, ``median``, ``std`` (sample, ddof=1; NaN for one value),
        ``minimum``, ``maximum``, ``q1``, ``q3`` and ``sum``. The sum is only
        meaningful for additive count metrics.

    Raises:
        AnalysisError: If the column is unknown or has no valid values.
    """
    all_values = numeric_series(data, metric_column)
    values = all_values.dropna()

    if values.empty:
        raise AnalysisError(f"No valid numeric values for {metric_column}")

    return {
        "count": int(values.count()),
        "missing": int(len(all_values) - len(values)),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "q1": float(values.quantile(0.25)),
        "q3": float(values.quantile(0.75)),
        "sum": float(values.sum()),
    }
