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
