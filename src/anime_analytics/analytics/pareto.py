"""Pareto (ranked-group concentration) analysis."""

import pandas as pd

from anime_analytics.analytics.metrics import numeric_series, validate_positive_int
from anime_analytics.exceptions import AnalysisError


def calculate_pareto(
    anime_data: pd.DataFrame,
    metric_column: str,
    n: int = 10,
) -> pd.Series:
    """Split ranked observations into ``n`` groups and report each group's share.

    Algorithm:
        1. Keep rows with a valid numeric value; sort them by the metric in
           descending order.
        2. Rank them with ``rank(method="first", ascending=False)`` so tied
           values still get distinct ranks.
        3. Cut the ranks into ``n`` approximately equal-sized groups with
           ``pd.qcut``.
        4. Divide each group's sum by the overall total.
        5. Sort the proportions in descending order and label them
           ``Group 1`` .. ``Group n``.

    The groups hold (almost) the same *number of anime*, not the same share
    of the metric. The result shows how concentrated the metric is; it does
    not assume or guarantee an 80/20 split. Because labels are assigned after
    sorting by proportion, ``Group 1`` is always the largest share. This only
    differs from rank order when tied values make a lower-ranked group larger
    (for example a middle group that received one extra row).

    Missing and non-numeric values are excluded, not treated as zero.

    Args:
        anime_data: DataFrame containing the metric column.
        metric_column: Name of a numeric column.
        n: Number of groups (positive integer, at most the number of valid
            observations).

    Returns:
        Series indexed ``Group 1`` .. ``Group n`` whose values sum to 1.0.

    Raises:
        AnalysisError: For an invalid ``n``, an unknown column, an empty
            dataset or no valid values, negative values, fewer valid
            observations than groups, or a total of zero.
    """
    n = validate_positive_int(n, "n")

    values = numeric_series(anime_data, metric_column)
    if anime_data.empty:
        raise AnalysisError("The dataset is empty")

    valid = values.dropna()
    if valid.empty:
        raise AnalysisError(f"No valid numeric values for {metric_column}")
    if (valid < 0).any():
        raise AnalysisError("Metric values must be non-negative for Pareto analysis")
    if len(valid) < n:
        raise AnalysisError(
            f"Cannot form {n} groups from {len(valid)} valid observations"
        )

    total = float(valid.sum())
    if total <= 0:
        raise AnalysisError("The metric total must be positive")

    ordered = valid.sort_values(ascending=False, kind="mergesort")
    ranks = ordered.rank(method="first", ascending=False)
    # Plain arrays avoid any index-alignment problems if the index has duplicates.
    group_ids = pd.qcut(ranks.to_numpy(), q=n, labels=False)

    proportions = ordered.groupby(group_ids, sort=True).sum() / total
    proportions = proportions.sort_values(ascending=False, kind="mergesort")
    proportions.index = pd.Index([f"Group {i}" for i in range(1, n + 1)])
    proportions.name = metric_column
    return proportions.astype("float64")
