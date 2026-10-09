"""Schemas shared by several endpoints."""

import math
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator


def _nan_to_none(value: Any) -> Any:
    """JSON cannot carry NaN/inf, so report them as null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


# A float that serialises NaN/inf as null.
OptionalFloat = Annotated[float | None, BeforeValidator(_nan_to_none)]


class ErrorResponse(BaseModel):
    """Body of every error response produced by the application."""

    detail: str


class RootResponse(BaseModel):
    name: str
    version: str
    environment: str
    docs: str
    openapi: str


class HealthResponse(BaseModel):
    status: str
    dataset_loaded: bool
    anime_count: int | None = None
