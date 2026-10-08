import pandas as pd


def describe_metric(data: pd.DataFrame, metric_column: str) -> dict:
    if metric_column not in data.columns:
        raise ValueError(f"Unsupported metric: {metric_column}")

    values = pd.to_numeric(data[metric_column], errors="coerce").dropna()

    if values.empty:
        raise ValueError(f"No valid numeric values for {metric_column}")

    return {
        "count": int(values.count()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
    }
