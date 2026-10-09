"""Service layer for analytics.

Services turn analytical results (DataFrames and Series) into response
schemas. They contain no HTTP code and no statistics of their own.
"""

import pandas as pd

from anime_analytics.analytics.aggregation import (
    aggregate_by_genre,
    aggregate_by_type,
)
from anime_analytics.analytics.descriptive import describe_metric
from anime_analytics.analytics.distribution import analyze_metric_distribution
from anime_analytics.analytics.engagement import summarize_engagement_by_type
from anime_analytics.analytics.metrics import get_metric, numeric_series
from anime_analytics.analytics.pareto import calculate_pareto
from anime_analytics.analytics.ranking import rank_top_n
from anime_analytics.exceptions import AnalysisError
from anime_analytics.repositories.anime_repository import AnimeRepository, to_records
from anime_analytics.schemas.analytics import (
    DataQuality,
    DistributionResponse,
    EngagementResponse,
    EngagementStats,
    GroupProportion,
    GroupStats,
    GroupStatsResponse,
    MetricSummary,
    OverviewResponse,
    ParetoResponse,
    TopAnimeItem,
    TopAnimeResponse,
)

OVERVIEW_METRICS = (
    "Score",
    "Episodes",
    "Members",
    "Favorites",
    "Watching",
    "Completed",
    "On-Hold",
    "Dropped",
    "Plan to Watch",
)


class AnalyticsService:
    """Use cases for the analytics endpoints."""

    def __init__(self, repository: AnimeRepository) -> None:
        self._repository = repository

    def _summary(self, metric: str) -> MetricSummary | None:
        """Summary for ``metric`` or ``None`` when it has no valid values."""
        try:
            stats = describe_metric(self._repository.data, metric)
        except AnalysisError:
            return None
        if get_metric(metric).kind != "count":
            stats["sum"] = float("nan")  # a sum of scores or ranks is meaningless
        return MetricSummary.model_validate(stats)

    def overview(self) -> OverviewResponse:
        """Dataset-wide summary statistics and data-quality information."""
        data = self._repository.data
        report = self._repository.report

        types = data["Type"].astype("string").fillna("Unknown")
        genres = data["Genres"].dropna().str.split(",").explode().str.strip()

        metrics: dict[str, MetricSummary] = {}
        for metric in OVERVIEW_METRICS:
            summary = self._summary(metric)
            if summary is not None:
                metrics[metric] = summary

        return OverviewResponse(
            total_anime=len(data),
            type_counts={
                str(name): int(count) for name, count in types.value_counts().items()
            },
            genre_count=int(genres[genres != ""].nunique()),
            data_quality=DataQuality(
                rows_raw=report.rows_raw,
                rows_clean=report.rows_clean,
                invalid_id_rows_removed=report.invalid_id_rows_removed,
                duplicate_ids_removed=report.duplicate_ids_removed,
                invalid_values_set_missing=report.invalid_values_set_missing,
            ),
            metrics=metrics,
        )

    def top_anime(self, metric: str, limit: int, order: str | None) -> TopAnimeResponse:
        """Rank anime by a metric.

        When ``order`` is ``None`` the best titles come first: highest value
        first, except for rank-type metrics (``Ranked``, ``Popularity``) where
        a lower number is better.
        """
        info = get_metric(metric)
        if order is None:
            order = "asc" if info.kind == "rank" else "desc"

        ranked = rank_top_n(
            self._repository.data, metric, limit, ascending=(order == "asc")
        )
        items = [
            TopAnimeItem(
                rank=r["rank"],
                mal_id=r["MAL_ID"],
                name=r.get("Name"),
                type=r.get("Type"),
                value=r["value"],
            )
            for r in to_records(ranked)
        ]
        return TopAnimeResponse(
            metric=metric, order=order, limit=limit, count=len(items), items=items
        )

    def _group_stats(
        self,
        frame: pd.DataFrame,
        key: str,
        metric: str,
        group_by: str,
        sort_by: str,
        order: str,
        limit: int,
    ) -> GroupStatsResponse:
        additive = get_metric(metric).kind == "count"
        items = [
            GroupStats(
                name=str(record[key]),
                anime_count=int(record["anime_count"]),
                total=record["total"] if additive else None,
                mean=record["mean"],
                median=record["median"],
            )
            for record in to_records(frame.head(limit))
        ]
        return GroupStatsResponse(
            metric=metric,
            group_by=group_by,
            sort_by=sort_by,
            order=order,
            count=len(items),
            items=items,
        )

    def _resolve_sort(self, metric: str, sort_by: str | None) -> str:
        additive = get_metric(metric).kind == "count"
        if sort_by is None:
            return "total" if additive else "mean"
        if sort_by == "total" and not additive:
            raise AnalysisError(
                f"'total' is only available for additive count metrics, not {metric}"
            )
        return sort_by

    def genres(
        self,
        metric: str,
        sort_by: str | None,
        order: str,
        min_anime: int,
        limit: int,
    ) -> GroupStatsResponse:
        """Aggregate a metric by genre (each anime counts in every genre it has)."""
        sort_by = self._resolve_sort(metric, sort_by)
        frame = aggregate_by_genre(
            self._repository.data,
            metric,
            sort_by=sort_by,
            ascending=(order == "asc"),
            min_count=min_anime,
        )
        return self._group_stats(frame, "genre", metric, "genre", sort_by, order, limit)

    def types(
        self,
        metric: str,
        sort_by: str | None,
        order: str,
        min_anime: int,
    ) -> GroupStatsResponse:
        """Compare anime formats (TV, Movie, OVA, ...) on a metric."""
        sort_by = self._resolve_sort(metric, sort_by)
        frame = aggregate_by_type(
            self._repository.data,
            metric,
            sort_by=sort_by,
            ascending=(order == "asc"),
            min_count=min_anime,
        )
        return self._group_stats(
            frame, "Type", metric, "type", sort_by, order, limit=len(frame)
        )

    def engagement(self, min_members: int) -> EngagementResponse:
        """Average engagement rates for each anime type."""
        frame = summarize_engagement_by_type(
            self._repository.data, min_members=min_members
        )
        items = [
            EngagementStats(
                type=str(r["Type"]),
                anime_count=int(r["anime_count"]),
                total_members=r["total_members"],
                mean_completion_rate=r["mean_completion_rate"],
                mean_drop_rate=r["mean_drop_rate"],
                mean_favorite_rate=r["mean_favorite_rate"],
            )
            for r in to_records(frame)
        ]
        return EngagementResponse(
            min_members=min_members, count=len(items), items=items
        )

    def distribution(self, metric: str, bins: int) -> DistributionResponse:
        """Distribution statistics and histogram for a metric."""
        result = analyze_metric_distribution(self._repository.data, metric, bins)
        return DistributionResponse.model_validate(result)

    def pareto(self, metric: str, n: int) -> ParetoResponse:
        """Share of a metric's total held by each of ``n`` ranked groups."""
        data = self._repository.data
        proportions = calculate_pareto(data, metric, n)
        values = numeric_series(data, metric)
        cumulative = proportions.cumsum()

        return ParetoResponse(
            metric=metric,
            groups=n,
            observations=int(values.notna().sum()),
            excluded_missing=int(values.isna().sum()),
            total=float(values.sum()),
            results=[
                GroupProportion(
                    group=str(group),
                    proportion=float(share),
                    cumulative_proportion=float(running),
                )
                for (group, share), running in zip(
                    proportions.items(), cumulative, strict=True
                )
            ],
        )
