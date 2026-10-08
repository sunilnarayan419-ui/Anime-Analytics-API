from fastapi import FastAPI

from anime_analytics.api.routes import anime, analytics
from anime_analytics.config import settings

app = FastAPI(
    title=settings.app_name,
    description="REST API for anime data analytics.",
    version="0.1.0",
)

app.include_router(anime.router)
app.include_router(analytics.router)


@app.get("/", tags=["General"])
def root() -> dict[str, str]:
    return {
        "message": "Welcome to Anime Analytics API",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
