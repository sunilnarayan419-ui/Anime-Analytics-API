"""Genre and category aggregation functions."""

import pandas as pd


def aggregate_by_genre(
    data: pd.DataFrame,
    metric_column: str,
) -> pd.Series:
    """
    Aggregate a metric by genre.

    Each anime can have multiple genres separated by commas. This function
    splits genres and sums metrics proportionally across them.

    Args:
        data: Cleaned anime DataFrame.
        metric_column: Numeric column to aggregate (e.g. "Completed", "Members").

    Returns:
        Series indexed by genre name, values are sums of the metric.

    Raises:
        ValueError: If columns are missing or metric has no valid data.
    """
    if metric_column not in data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    if "Genres" not in data.columns:
        raise ValueError("Genres column not found in data")

    values = pd.to_numeric(data[metric_column], errors="coerce").dropna()

    if values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    genre_sums: dict[str, float] = {}

    for _, row in data.iterrows():
        genre_str = str(row["Genres"])
        metric_val = row[metric_column]

        # Skip NaN values
        if pd.isna(metric_val):
            continue

        # Split genres by comma and strip whitespace
        genres = [g.strip() for g in genre_str.split(",") if g.strip()]

        if not genres:
            continue

        # Distribute the metric value equally across all listed genres
        share = metric_val / len(genres)
        for g in genres:
            genre_sums[g] = genre_sums.get(g, 0.0) + share

    # Sort by total in descending order
    result = pd.Series(genre_sums).sort_values(ascending=False)

    return result


def aggregate_by_type(
    data: pd.DataFrame,
    metric_column: str,
) -> pd.Series:
    """
    Aggregate a metric by anime type (TV, Movie, OVA, etc.).

    Args:
        data: Cleaned anime DataFrame.
        metric_column: Numeric column to aggregate.

    Returns:
        Series indexed by Type, values are sums of the metric.

    Raises:
        ValueError: If columns are missing or metric has no valid data.
    """
    if metric_column not in data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    if "Type" not in data.columns:
        raise ValueError("Type column not found in data")

    values = pd.to_numeric(data[metric_column], errors="coerce").dropna()

    if values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    return data.groupby("Type")[metric_column].sum().sort_values(ascending=False)


def aggregate_by_category(
    data: pd.DataFrame,
    category_column: str,
    metric_column: str,
) -> pd.Series:
    """
    Generic aggregation by any category column.

    Args:
        data: Cleaned anime DataFrame.
        category_column: Column to group by.
        metric_column: Numeric column to aggregate.

    Returns:
        Series indexed by category, values are sums of the metric.

    Raises:
        ValueError: If columns are missing or invalid.
    """
    if metric_column not in data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    if category_column not in data.columns:
        raise ValueError(f"Unknown category column: {category_column}")

    values = pd.to_numeric(data[metric_column], errors="coerce").dropna()

    if values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    return data.groupby(category_column)[metric_column].sum().sort_values(ascending=False)