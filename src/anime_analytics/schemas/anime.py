from pydantic import BaseModel


class AnimeResponse(BaseModel):
    MAL_ID: int
    Name: str
