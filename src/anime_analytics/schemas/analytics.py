"""Response schemas for the analytics endpoints.

Analytical results use snake_case field names. Only anime *records* mirror
the dataset's column names (see ``schemas/anime.py``).
"""

from pydantic import BaseModel, Field

from anime_analytics.schemas.common import OptionalFloat


class MetricSummary(BaseModel):
    """Descriptive statistics for one metric."""

    count: int = Field(description="Valid (non-missing) values")
    missing: int = Field(description="Rows without a valid value")
    mean: OptionalFloat
    median: OptionalFloat
    std: OptionalFloat
    minimum: OptionalFloat
    maximum: OptionalFloat
    q1: OptionalFloat
    q3: OptionalFloat
    sum: OptionalFloat = Field(
        None, description="Only present for additive count metrics"
    )


class DataQuality(BaseModel):
    """What the preprocessing step did to the raw file."""

    rows_raw: int
    rows_clean: int
    invalid_id_rows_removed: int
    duplicate_ids_removed: int
    invalid_values_set_missing: dict[str, int]


class OverviewResponse(BaseModel):
    total_anime: int
    type_counts: dict[str, int]
    genre_count: int
    data_quality: DataQuality
    metrics: dict[str, MetricSummary]


class TopAnimeItem(BaseModel):
    rank: int
    mal_id: int
    name: str | None
    type: str | None
    value: OptionalFloat


class TopAnimeResponse(BaseModel):
    metric: str
    order: str
    limit: int
    count: int
    items: list[TopAnimeItem]


class GroupStats(BaseModel):
    """Aggregated metric values for one genre or type."""

    name: str
    anime_count: int = Field(description="Anime with a valid metric value")
    total: OptionalFloat = Field(
        None, description="Sum of the metric; only for additive count metrics"
    )
    mean: OptionalFloat
    median: OptionalFloat


class GroupStatsResponse(BaseModel):
    metric: str
    group_by: str
    sort_by: str
    order: str
    count: int
    items: list[GroupStats]


class EngagementStats(BaseModel):
    type: str
    anime_count: int
    total_members: OptionalFloat
    mean_completion_rate: OptionalFloat
    mean_drop_rate: OptionalFloat
    mean_favorite_rate: OptionalFloat


class EngagementResponse(BaseModel):
    min_members: int
    count: int
    items: list[EngagementStats]


class HistogramBin(BaseModel):
    lower: float
    upper: float
    count: int


class DistributionResponse(BaseModel):
    metric: str
    count: int
    missing: int
    min: float
    max: float
    mean: float
    median: float
    std: OptionalFloat
    percentiles: dict[str, float]
    skewness: OptionalFloat
    kurtosis: OptionalFloat
    histogram: list[HistogramBin]


class GroupProportion(BaseModel):
    group: str
    proportion: float
    cumulative_proportion: float


class ParetoResponse(BaseModel):
    metric: str
    groups: int
    observations: int = Field(description="Anime with a valid metric value")
    excluded_missing: int = Field(description="Anime excluded for a missing value")
    total: float = Field(description="Sum of the metric over all observations")
    results: list[GroupProportion]
