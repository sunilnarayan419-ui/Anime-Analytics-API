import pandas as pd


NUMERIC_COLUMNS = {
    "Score": float,
    "Episodes": int,
    "Ranked": float,
    "Popularity": int,
    "Members": int,
    "Favorites": int,
    "Watching": int,
    "Completed": int,
    "On-Hold": int,
    "Dropped": int,
    "Plan to Watch": int,
    "Score-10": float,
    "Score-9": float,
    "Score-8": float,
    "Score-7": float,
    "Score-6": float,
    "Score-5": float,
    "Score-4": float,
    "Score-3": float,
    "Score-2": float,
    "Score-1": float,
}

REQUIRED_COLUMNS = {"MAL_ID", "Name"}

CATEGORICAL_COLUMNS = {
    "Type",
    "Rating",
    "Genres",
    "Source",
    "Duration",
    "Aired",
    "Premiered",
    "Producers",
    "Licensors",
    "Studios",
    "English name",
    "Japanese name",
}


def preprocess_anime(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the anime dataset.

    Steps:
    1. Validate required columns are present.
    2. Remove duplicate MAL_ID entries (keep first).
    3. Convert numeric columns, treating "Unknown" as NaN.
    4. Ensure categorical columns are strings.
    5. Return a clean copy without mutating the source data.

    Args:
        data: Raw DataFrame loaded from CSV.

    Returns:
        Cleaned DataFrame with proper dtypes.

    Raises:
        ValueError: If required columns are missing.
    """
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = data.copy()

    # Remove duplicates by MAL_ID, keeping first occurrence
    result = result.drop_duplicates(subset=["MAL_ID"], keep="first")

    # Convert numeric columns: "Unknown" -> NaN, then to proper dtype
    for col, dtype in NUMERIC_COLUMNS.items():
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")
            if dtype is int:
                result[col] = result[col].astype("Int64")
            else:
                result[col] = result[col].astype(dtype)

    # Ensure categorical columns are strings
    for col in CATEGORICAL_COLUMNS:
        if col in result.columns:
            result[col] = result[col].astype(str)

    return result


def validate_numeric_columns(data: pd.DataFrame) -> list[str]:
    """
    Identify which numeric columns have at least one non-null value.

    Args:
        data: Cleaned DataFrame.

    Returns:
        List of numeric column names with at least one non-null value.
    """
    available: list[str] = []
    for col, dtype in NUMERIC_COLUMNS.items():
        if col in data.columns and data[col].notna().any():
            available.append(col)
    return available
