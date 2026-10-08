"""Metric distribution analysis."""

import pandas as pd


def analyze_metric_distribution(
    data: pd.DataFrame, metric_column: str, bins: int = 10
) -> dict:
    """
    Analyze the distribution of a numeric metric.

    Args:
        data: Cleaned anime DataFrame.
        metric_column: Column name containing numeric values.
        bins: Number of bins for histogram analysis.

    Returns:
        Dictionary with distribution statistics and percentiles.

    Raises:
        ValueError: If column is not found or has no valid numeric data.
    """
    if metric_column not in data.columns:
        raise ValueError(f"Unsupported metric: {metric_column}")

    values = pd.to_numeric(data[metric_column], errors="coerce").dropna()

    if values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    # Calculate percentiles
    percentiles = values.quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).to_dict()

    # Calculate histogram bins (using numpy if available, otherwise pandas)
    try:
        import numpy as np

        hist, bin_edges = np.histogram(values, bins=bins)
        bin_labels = [
            f"{bin_edges[i]:.1f} - {bin_edges[i + 1]:.1f}"
            for i in range(len(bin_edges) - 1)
        ]
        bin_counts = hist.tolist()
    except ImportError:
        # Fallback to pandas value_counts for bins
        binned = pd.cut(values, bins=bins)
        bin_counts = binned.value_counts().sort_index().tolist()
        bin_labels = [str(interval) for interval in binned.cat.categories]

    # Calculate skewness and kurtosis
    try:
        from scipy import stats

        skewness = float(stats.skew(values))
        kurtosis = float(stats.kurtosis(values))
    except ImportError:
        skewness = 0.0
        kurtosis = 0.0

    return {
        "metric": metric_column,
        "count": int(len(values)),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()),
        "percentiles": {f"p{p}": float(p) for p, v in percentiles.items()},
        "histogram": {
            "bins": bin_labels,
            "counts": bin_counts,
        },
        "skewness": skewness,
        "kurtosis": kurtosis,
    }


def get_top_n_ranking(data: pd.DataFrame, metric_column: str, n: int = 10) -> pd.Series:
    """
    Get top N anime ranked by a specific metric.

    Args:
        data: Cleaned anime DataFrame.
        metric_column: Column name containing numeric values.
        n: Number of top entries to return.

    Returns:
        Series with MAL_ID as index and metric values as values, sorted descending.

    Raises:
        ValueError: If column is not found or n is invalid.
    """
    if metric_column not in data.columns:
        raise ValueError(f"Unsupported metric: {metric_column}")

    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")

    # Convert to numeric, handling "Unknown" values
    values = pd.to_numeric(data[metric_column], errors="coerce")

    # Sort by metric value descending
    ranked = values.sort_values(ascending=False)

    return ranked.head(n)