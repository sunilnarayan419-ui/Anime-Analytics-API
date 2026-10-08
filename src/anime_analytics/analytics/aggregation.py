import pandas as pd


def aggregate_by_column(
    data: pd.DataFrame,
    category_column: str,
    metric_column: str,
) -> pd.Series:
    if category_column not in data.columns:
        raise ValueError(f"Unknown category column: {category_column}")

    if metric_column not in data.columns:
        raise ValueError(f"Unknown metric column: {metric_column}")

    return data.groupby(category_column)[metric_column].sum().sort_values(
        ascending=False
    )
