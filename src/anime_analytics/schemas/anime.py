"""Schemas for anime records.

Field names in the JSON mirror the dataset's column names (for example
``MAL_ID`` and ``On-Hold``) so a record can be matched to the data
dictionary. ``Genres`` is returned as a list instead of a comma-separated
string.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnimeResponse(BaseModel):
    """One anime record."""

    model_config = ConfigDict(populate_by_name=True)

    mal_id: int = Field(alias="MAL_ID", description="MyAnimeList identifier")
    name: str | None = Field(None, alias="Name")
    score: float | None = Field(None, alias="Score")
    genres: list[str] = Field(default_factory=list, alias="Genres")
    english_name: str | None = Field(None, alias="English name")
    japanese_name: str | None = Field(None, alias="Japanese name")
    type: str | None = Field(None, alias="Type")
    episodes: int | None = Field(None, alias="Episodes")
    aired: str | None = Field(None, alias="Aired")
    premiered: str | None = Field(None, alias="Premiered")
    producers: str | None = Field(None, alias="Producers")
    licensors: str | None = Field(None, alias="Licensors")
    studios: str | None = Field(None, alias="Studios")
    source: str | None = Field(None, alias="Source")
    duration: str | None = Field(None, alias="Duration")
    rating: str | None = Field(None, alias="Rating")
    ranked: int | None = Field(None, alias="Ranked")
    popularity: int | None = Field(None, alias="Popularity")
    members: int | None = Field(None, alias="Members")
    favorites: int | None = Field(None, alias="Favorites")
    watching: int | None = Field(None, alias="Watching")
    completed: int | None = Field(None, alias="Completed")
    on_hold: int | None = Field(None, alias="On-Hold")
    dropped: int | None = Field(None, alias="Dropped")
    plan_to_watch: int | None = Field(None, alias="Plan to Watch")
    score_10: int | None = Field(None, alias="Score-10")
    score_9: int | None = Field(None, alias="Score-9")
    score_8: int | None = Field(None, alias="Score-8")
    score_7: int | None = Field(None, alias="Score-7")
    score_6: int | None = Field(None, alias="Score-6")
    score_5: int | None = Field(None, alias="Score-5")
    score_4: int | None = Field(None, alias="Score-4")
    score_3: int | None = Field(None, alias="Score-3")
    score_2: int | None = Field(None, alias="Score-2")
    score_1: int | None = Field(None, alias="Score-1")

    @field_validator("genres", mode="before")
    @classmethod
    def _split_genres(cls, value: Any) -> Any:
        if value is None:
            return []
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value


class AnimeListResponse(BaseModel):
    """A page of anime plus the information needed to request the next page."""

    total: int = Field(description="Number of anime matching the filters")
    limit: int
    offset: int
    count: int = Field(description="Number of anime in this page")
    items: list[AnimeResponse]


SortField = Literal[
    "MAL_ID",
    "Name",
    "Score",
    "Episodes",
    "Ranked",
    "Popularity",
    "Members",
    "Favorites",
    "Watching",
    "Completed",
    "On-Hold",
    "Dropped",
    "Plan to Watch",
]
SortOrder = Literal["asc", "desc"]
