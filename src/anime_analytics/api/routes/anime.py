from fastapi import APIRouter, HTTPException

from anime_analytics.repositories.anime_repository import get_anime_by_id

router = APIRouter(prefix="/anime", tags=["Anime"])


@router.get("/{mal_id}")
def get_anime(mal_id: int) -> dict:
    anime = get_anime_by_id(mal_id)

    if anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")

    return anime
