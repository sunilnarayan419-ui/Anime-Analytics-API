"""FastAPI dependencies that provide the repository and services."""

from typing import Annotated

from fastapi import Depends, Request

from anime_analytics.exceptions import DatasetUnavailableError
from anime_analytics.repositories.anime_repository import AnimeRepository
from anime_analytics.services.analytics_service import AnalyticsService
from anime_analytics.services.anime_service import AnimeService


def get_repository(request: Request) -> AnimeRepository:
    """Return the repository created at startup.

    Raises:
        DatasetUnavailableError: If the dataset could not be loaded.
    """
    repository: AnimeRepository | None = request.app.state.repository
    if repository is None:
        raise DatasetUnavailableError(
            "The anime dataset is not available. Check the DATA_PATH setting "
            "(see data/README.md)."
        )
    return repository


RepositoryDep = Annotated[AnimeRepository, Depends(get_repository)]


def get_anime_service(repository: RepositoryDep) -> AnimeService:
    return AnimeService(repository)


def get_analytics_service(repository: RepositoryDep) -> AnalyticsService:
    return AnalyticsService(repository)


AnimeServiceDep = Annotated[AnimeService, Depends(get_anime_service)]
AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
