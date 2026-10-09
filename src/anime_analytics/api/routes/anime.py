"""Routes for anime records."""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Path, Query

from anime_analytics.api.dependencies import AnimeServiceDep
from anime_analytics.config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from anime_analytics.schemas.anime import (
    AnimeListResponse,
    AnimeResponse,
    SortField,
    SortOrder,
)
from anime_analytics.schemas.common import ErrorResponse

router = APIRouter(prefix="/anime", tags=["Anime"])

_UNAVAILABLE: dict[int | str, dict[str, Any]] = {
    503: {"model": ErrorResponse, "description": "Dataset not loaded"}
}


@router.get(
    "",
    response_model=AnimeListResponse,
    summary="List anime",
    responses=_UNAVAILABLE,
)
def list_anime(
    service: AnimeServiceDep,
    anime_type: Annotated[
        str | None,
        Query(max_length=50, description="Exact type, e.g. TV, Movie, OVA"),
    ] = None,
    genre: Annotated[
        str | None,
        Query(max_length=50, description="Exact genre name, e.g. Action"),
    ] = None,
    name: Annotated[
        str | None,
        Query(max_length=100, description="Case-insensitive title search"),
    ] = None,
    min_score: Annotated[float | None, Query(ge=0, le=10)] = None,
    max_score: Annotated[float | None, Query(ge=0, le=10)] = None,
    sort_by: SortField = "MAL_ID",
    order: SortOrder = "asc",
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AnimeListResponse:
    """List anime with optional filters, sorting and pagination.

    Filters are combined with AND. Anime with a missing value in the sort
    column are listed last.
    """
    if min_score is not None and max_score is not None and min_score > max_score:
        raise HTTPException(
            status_code=422, detail="min_score cannot be greater than max_score"
        )
    return service.list_anime(
        anime_type=anime_type,
        genre=genre,
        name=name,
        min_score=min_score,
        max_score=max_score,
        sort_by=sort_by,
        ascending=(order == "asc"),
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{mal_id}",
    response_model=AnimeResponse,
    summary="Get one anime",
    responses={404: {"model": ErrorResponse}, **_UNAVAILABLE},
)
def get_anime(
    service: AnimeServiceDep,
    mal_id: Annotated[int, Path(ge=1, description="MyAnimeList identifier")],
) -> AnimeResponse:
    """Return a single anime by its MyAnimeList identifier."""
    anime = service.get_anime(mal_id)
    if anime is None:
        raise HTTPException(status_code=404, detail=f"Anime {mal_id} not found")
    return anime
