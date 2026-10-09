"""Metric distribution analysis."""

from typing import Any, cast

import numpy as np
import pandas as pd

from anime_analytics.analytics.metrics import numeric_series, validate_positive_int
from anime_analytics.exceptions import AnalysisError

MAX_BINS = 100
PERCENTILES: tuple[int, ...] = (25, 50, 75, 90, 95, 99)


def analyze_metric_distribution(
    data: pd.DataFrame,
    metric_column: str,
    bins: int = 10,
) -> dict[str, Any]:
    """Describe how the values of a metric are distributed.

    The histogram uses ``bins`` equal-width bins between the observed minimum
    and maximum. Skewness is the bias-corrected sample skewness and kurtosis
    is the bias-corrected *excess* kurtosis (0 for a normal distribution);
    both are NaN when there are too few observations (fewer than 3 and 4).

    Raises:
        AnalysisError: If the column is unknown, has no valid values, or
            ``bins`` is not an integer between 1 and ``MAX_BINS``.
    """
    bins = validate_positive_int(bins, "bins")
    if bins > MAX_BINS:
        raise AnalysisError(f"bins must be at most {MAX_BINS}")

    all_values = numeric_series(data, metric_column)
    values = all_values.dropna()

    if values.empty:
        raise AnalysisError(f"No valid numeric values for {metric_column}")

    counts, edges = np.histogram(values.to_numpy(), bins=bins)
    percentile_values = np.percentile(values.to_numpy(), PERCENTILES)

    return {
        "metric": metric_column,
        "count": int(values.count()),
        "missing": int(len(all_values) - len(values)),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()),
        "percentiles": {
            f"p{level}": float(value)
            for level, value in zip(PERCENTILES, percentile_values, strict=True)
        },
        "skewness": float(cast(float, values.skew())),
        "kurtosis": float(cast(float, values.kurt())),
        "histogram": [
            {
                "lower": float(edges[i]),
                "upper": float(edges[i + 1]),
                "count": int(counts[i]),
            }
            for i in range(len(counts))
        ],
    }
