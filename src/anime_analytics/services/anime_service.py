"""Service layer for anime records."""

from anime_analytics.repositories.anime_repository import AnimeRepository, to_records
from anime_analytics.schemas.anime import AnimeListResponse, AnimeResponse


class AnimeService:
    """Use cases for retrieving anime records."""

    def __init__(self, repository: AnimeRepository) -> None:
        self._repository = repository

    def get_anime(self, mal_id: int) -> AnimeResponse | None:
        """Return one anime, or ``None`` if the id does not exist."""
        record = self._repository.get_by_id(mal_id)
        return None if record is None else AnimeResponse.model_validate(record)

    def list_anime(
        self,
        *,
        anime_type: str | None = None,
        genre: str | None = None,
        name: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        sort_by: str = "MAL_ID",
        ascending: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> AnimeListResponse:
        """Return one page of anime matching the filters."""
        total, page = self._repository.query(
            anime_type=anime_type,
            genre=genre,
            name=name,
            min_score=min_score,
            max_score=max_score,
            sort_by=sort_by,
            ascending=ascending,
            limit=limit,
            offset=offset,
        )
        items = [AnimeResponse.model_validate(r) for r in to_records(page)]
        return AnimeListResponse(
            total=total,
            limit=limit,
            offset=offset,
            count=len(items),
            items=items,
        )
