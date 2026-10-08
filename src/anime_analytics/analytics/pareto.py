import pandas as pd


def calculate_pareto(
    anime_data: pd.DataFrame,
    metric_column: str,
    n: int = 10,
) -> pd.Series:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")

    if metric_column not in anime_data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    values = pd.to_numeric(anime_data[metric_column], errors="coerce")

    if values.isna().any():
        raise ValueError("Metric contains missing or non-numeric values")

    if (values < 0).any():
        raise ValueError("Metric values must be non-negative")

    if len(values) < n:
        raise ValueError("Number of observations must be at least n")

    total = values.sum()

    if total <= 0:
        raise ValueError("Metric total must be positive")

    ranks = values.rank(method="first", ascending=False)

    groups = pd.qcut(ranks, q=n, labels=False)

    proportions = values.groupby(groups).sum() / total
    proportions = proportions.sort_values(ascending=False)

    proportions.index = [
        f"Group {i + 1}" for i in range(len(proportions))
    ]

    return proportions
