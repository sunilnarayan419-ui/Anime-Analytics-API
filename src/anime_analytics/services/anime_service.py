"""Service layer for anime record operations."""

from anime_analytics.repositories.anime_repository import (
    get_anime_by_id,
    get_anime_list,
    load_anime_data,
)


def get_anime(mal_id: int) -> dict | None:
    """
    Get a single anime by MAL ID.

    Args:
        mal_id: MyAnimeList ID.

    Returns:
        Anime dictionary if found, None otherwise.
    """
    return get_anime_by_id(mal_id)


def list_anime(
    anime_type: str | None = None,
    genre: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """
    List anime with optional filtering.

    Args:
        anime_type: Filter by Type (e.g., "TV", "Movie").
        genre: Filter by genre (case-insensitive partial match).
        limit: Maximum number of results.
        offset: Number of results to skip.

    Returns:
        List of anime dictionaries.
    """
    data = load_anime_data()
    df = get_anime_list(
        data=data,
        anime_type=anime_type,
        genre=genre,
        limit=limit,
        offset=offset,
    )
    # Convert DataFrame to list of dicts, handling NA values
    return df.where(pd.notna(df), None).to_dict("records")


def get_overview() -> dict:
    """
    Get overview statistics of the anime dataset.

    Returns:
        Dictionary with dataset summary statistics.
    """
    data = load_anime_data()
    numeric_cols = [col for col in data.columns
                   if data[col].dtype in ["int64", "float64", "Int64"]]

    overview = {
        "total_anime": len(data),
        "unique_types": data["Type"].nunique() if "Type" in data.columns else 0,
        "metrics": {}
    }

    # Calculate basic stats for key metrics
    key_metrics = ["Members", "Completed", "Favorites", "Score", "Episodes"]
    for metric in key_metrics:
        if metric in data.columns and data[metric].notna().any():
            values = pd.to_numeric(data[metric], errors="coerce").dropna()
            if len(values) > 0:
                overview["metrics"][metric] = {
                    "mean": float(values.mean()),
                    "median": float(values.median()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "total": float(values.sum()) if metric in ["Members", "Completed", "Favorites"] else None,
                    "count": int(len(values)),
                }

    return overview
