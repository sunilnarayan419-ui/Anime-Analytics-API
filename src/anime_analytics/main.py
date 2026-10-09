"""Application factory and entry point.

Run with::

    uvicorn anime_analytics.main:app --app-dir src
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from anime_analytics import __version__
from anime_analytics.api.routes import analytics, anime
from anime_analytics.config import Settings, get_settings
from anime_analytics.exceptions import (
    AnalysisError,
    DatasetError,
    DatasetUnavailableError,
)
from anime_analytics.repositories.anime_repository import AnimeRepository
from anime_analytics.schemas.common import HealthResponse, RootResponse

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    """Configure application logging (idempotent)."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("anime_analytics").setLevel(level)


def _load_repository(settings: Settings) -> AnimeRepository | None:
    """Load the dataset, or return ``None`` (and log why) if that fails."""
    try:
        return AnimeRepository.from_csv(settings.data_path)
    except DatasetError as exc:
        logger.error("Dataset could not be loaded: %s", exc)
        return None


def create_app(
    settings: Settings | None = None,
    repository: AnimeRepository | None = None,
) -> FastAPI:
    """Create the FastAPI application.

    Args:
        settings: Settings to use; defaults to the environment-based settings.
        repository: A ready repository (used by tests). When omitted, the
            dataset is loaded from ``settings.data_path`` at startup. If that
            fails the application still starts, ``/health`` reports the
            problem and data endpoints answer 503.
    """
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if app.state.repository is None:
            app.state.repository = _load_repository(settings)
        yield

    app = FastAPI(
        title=settings.app_name,
        description="REST API for analysing the MyAnimeList anime dataset.",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.repository = repository

    @app.exception_handler(AnalysisError)
    async def _analysis_error(_: Request, exc: AnalysisError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(DatasetUnavailableError)
    async def _dataset_unavailable(
        _: Request, exc: DatasetUnavailableError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    app.include_router(anime.router)
    app.include_router(analytics.router)

    @app.get("/", response_model=RootResponse, tags=["General"], summary="API info")
    def root() -> RootResponse:
        return RootResponse(
            name=settings.app_name,
            version=__version__,
            environment=settings.app_env,
            docs="/docs",
            openapi="/openapi.json",
        )

    @app.get(
        "/health", response_model=HealthResponse, tags=["General"], summary="Health"
    )
    def health_check(request: Request) -> HealthResponse:
        """Report liveness and whether the dataset is loaded."""
        repo: AnimeRepository | None = request.app.state.repository
        if repo is None:
            return HealthResponse(status="degraded", dataset_loaded=False)
        return HealthResponse(status="ok", dataset_loaded=True, anime_count=len(repo))

    return app


app = create_app()
