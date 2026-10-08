import pandas as pd


def preprocess_anime(data: pd.DataFrame) -> pd.DataFrame:
    required_columns = {"MAL_ID", "Name"}

    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = data.copy()
    result = result.drop_duplicates(subset=["MAL_ID"], keep="first")

    return result
