from functools import lru_cache

import pandas as pd

from anime_analytics.analytics.preprocessing import preprocess_anime
from anime_analytics.config import settings


@lru_cache(maxsize=1)
def load_anime_data() -> pd.DataFrame:
    try:
        data = pd.read_csv(settings.data_path)
    except FileNotFoundError as exc:
        raise ValueError(
            f"Dataset not found at '{settings.data_path}'. "
            "Place anime.csv in the data directory."
        ) from exc

    return preprocess_anime(data)


def get_anime_by_id(mal_id: int) -> dict | None:
    data = load_anime_data()
    matches = data.loc[data["MAL_ID"] == mal_id]

    if matches.empty:
        return None

    return matches.iloc[0].where(pd.notna(matches.iloc[0]), None).to_dict()


def get_anime_list(
    data: pd.DataFrame | None = None,
    anime_type: str | None = None,
    genre: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:
    """
    Return a paginated, optionally filtered view of the anime dataset.

    Args:
        data: Preprocessed anime DataFrame. Loads from repository if None.
        anime_type: Filter by Type (e.g. "TV", "Movie").
        genre: Filter by genre (case-insensitive, partial match on Genres).
        limit: Maximum number of rows to return.
        offset: Number of rows to skip.

    Returns:
        DataFrame slice with applied filters.
    """
    if data is None:
        data = load_anime_data()

    result = data.copy()

    if anime_type:
        result = result[result["Type"] == anime_type]

    if genre:
        g = genre.lower()
        result = result[result["Genres"].str.lower().str.contains(g, na=False)]

    return result.iloc[offset : offset + limit]
