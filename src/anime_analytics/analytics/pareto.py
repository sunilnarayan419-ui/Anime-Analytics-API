"""Pareto analysis for metric distribution across ranked groups."""

import pandas as pd


def calculate_pareto(
    anime_data: pd.DataFrame,
    metric_column: str,
    n: int = 10,
) -> pd.Series:
    """
    Perform Pareto analysis by dividing ranked observations into groups.

    The function:
    1. Sorts observations by the metric in descending order.
    2. Ranks values using rank(method="first") for tie-breaking.
    3. Divides observations into n equal-sized groups using pd.qcut.
    4. Calculates each group's metric sum as a proportion of total.
    5. Returns proportions sorted descending.

    Args:
        anime_data: Cleaned anime DataFrame.
        metric_column: Column name with numeric values.
        n: Number of groups for decile analysis.

    Returns:
        Series with "Group 1" through "Group n" labels and proportions.

    Raises:
        ValueError: For invalid parameters, unknown columns, or data issues.
    """
    # Validate n
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")

    # Validate metric column exists
    if metric_column not in anime_data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    # Convert to numeric, which will produce NaN for "Unknown" values
    values = pd.to_numeric(anime_data[metric_column], errors="coerce")

    # Drop NaN values (not raise error - just filter them out)
    valid_values = values.dropna()

    if valid_values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    # Check for negative values (not meaningful for Pareto)
    if (valid_values < 0).any():
        raise ValueError("Metric values must be non-negative")

    # Check we have enough observations
    if len(valid_values) < n:
        raise ValueError("Number of observations must be at least n")

    total = valid_values.sum()

    # Handle zero total case
    if total <= 0:
        raise ValueError("Metric total must be positive")

    # Rank in descending order (highest gets rank 1)
    ranks = valid_values.rank(method="first", ascending=False)

    # Divide into n equal-sized groups
    groups = pd.qcut(ranks, q=n, labels=False, duplicates="drop")

    # Calculate each group's sum as proportion of total
    proportions = valid_values.groupby(groups, sort=False).sum() / total

    # Sort proportions descending
    proportions = proportions.sort_values(ascending=False)

    # Rename index to "Group 1", "Group 2", etc.
    proportions.index = [f"Group {i + 1}" for i in range(len(proportions))]

    return proportions
