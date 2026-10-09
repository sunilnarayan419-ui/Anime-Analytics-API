"""Routes for analytics."""

from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query

from anime_analytics.analytics.distribution import MAX_BINS
from anime_analytics.analytics.metrics import CountMetricName, MetricName
from anime_analytics.api.dependencies import AnalyticsServiceDep
from anime_analytics.schemas.analytics import (
    DistributionResponse,
    EngagementResponse,
    GroupStatsResponse,
    OverviewResponse,
    ParetoResponse,
    TopAnimeResponse,
)
from anime_analytics.schemas.anime import SortOrder
from anime_analytics.schemas.common import ErrorResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={
        400: {"model": ErrorResponse, "description": "Analysis cannot be performed"},
        503: {"model": ErrorResponse, "description": "Dataset not loaded"},
    },
)

GroupSortField = Literal["total", "mean", "median", "anime_count"]
MAX_GROUPS = 100


@router.get("/overview", response_model=OverviewResponse, summary="Dataset overview")
def overview(service: AnalyticsServiceDep) -> OverviewResponse:
    """Summary statistics for the main metrics plus data-quality counts."""
    return service.overview()


@router.get("/top-anime", response_model=TopAnimeResponse, summary="Top anime")
def top_anime(
    service: AnalyticsServiceDep,
    metric: MetricName = "Members",
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    order: Annotated[
        SortOrder | None,
        Query(
            description="Defaults to desc, or asc for rank metrics "
            "(Ranked, Popularity) where a lower number is better"
        ),
    ] = None,
) -> TopAnimeResponse:
    """Rank anime by a metric. Anime without a value for it are excluded."""
    return service.top_anime(metric, limit, order)


@router.get("/genres", response_model=GroupStatsResponse, summary="Genre analysis")
def genres(
    service: AnalyticsServiceDep,
    metric: MetricName = "Members",
    sort_by: Annotated[
        GroupSortField | None,
        Query(description="Defaults to total for count metrics, mean otherwise"),
    ] = None,
    order: SortOrder = "desc",
    min_anime: Annotated[
        int, Query(ge=1, description="Hide genres with fewer anime than this")
    ] = 1,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> GroupStatsResponse:
    """Aggregate a metric by genre.

    An anime is counted in full for every genre it lists, so genre totals add
    up to more than the dataset total.
    """
    return service.genres(metric, sort_by, order, min_anime, limit)


@router.get("/types", response_model=GroupStatsResponse, summary="Type comparison")
def types(
    service: AnalyticsServiceDep,
    metric: MetricName = "Members",
    sort_by: Annotated[
        GroupSortField | None,
        Query(description="Defaults to total for count metrics, mean otherwise"),
    ] = None,
    order: SortOrder = "desc",
    min_anime: Annotated[int, Query(ge=1)] = 1,
) -> GroupStatsResponse:
    """Compare anime formats (TV, Movie, OVA, ...) on a metric."""
    return service.types(metric, sort_by, order, min_anime)


@router.get(
    "/engagement", response_model=EngagementResponse, summary="Audience engagement"
)
def engagement(
    service: AnalyticsServiceDep,
    min_members: Annotated[
        int,
        Query(ge=0, description="Ignore anime with fewer members (reduces noise)"),
    ] = 0,
) -> EngagementResponse:
    """Average completion, drop and favorite rates for each anime type."""
    return service.engagement(min_members)


@router.get(
    "/distribution/{metric}",
    response_model=DistributionResponse,
    summary="Metric distribution",
)
def distribution(
    service: AnalyticsServiceDep,
    metric: Annotated[MetricName, Path(description="Metric to analyse")],
    bins: Annotated[int, Query(ge=1, le=MAX_BINS)] = 10,
) -> DistributionResponse:
    """Percentiles, moments and an equal-width histogram of a metric."""
    return service.distribution(metric, bins)


@router.get("/pareto", response_model=ParetoResponse, summary="Pareto analysis")
def pareto(
    service: AnalyticsServiceDep,
    metric: CountMetricName = "Completed",
    n: Annotated[
        int, Query(ge=1, le=MAX_GROUPS, description="Number of ranked groups")
    ] = 10,
) -> ParetoResponse:
    """Share of the metric's total held by each of ``n`` ranked groups.

    Groups contain (almost) equal numbers of anime, ranked from highest to
    lowest metric value. Only additive count metrics are supported.
    """
    return service.pareto(metric, n)
