"""Analytics service layer."""

from anime_analytics.analytics.aggregation import aggregate_by_genre, aggregate_by_type
from anime_analytics.analytics.descriptive import describe_metric
from anime_analytics.analytics.distribution import analyze_metric_distribution, get_top_n_ranking
from anime_analytics.analytics.pareto import calculate_pareto
from anime_analytics.repositories.anime_repository import load_anime_data


def run_pareto_analysis(metric_column: str, n: int):
    """Run Pareto analysis on the specified metric."""
    data = load_anime_data()
    return calculate_pareto(data, metric_column, n)


def run_descriptive_analysis(metric_column: str):
    """Calculate descriptive statistics for a metric."""
    data = load_anime_data()
    return describe_metric(data, metric_column)


def run_genre_aggregation(metric_column: str):
    """Aggregate metric by genre."""
    data = load_anime_data()
    return aggregate_by_genre(data, metric_column)


def run_type_aggregation(metric_column: str):
    """Aggregate metric by anime type."""
    data = load_anime_data()
    return aggregate_by_type(data, metric_column)


def run_top_n_ranking(metric_column: str, n: int = 10):
    """Get top N anime ranked by a metric."""
    data = load_anime_data()
    return get_top_n_ranking(data, metric_column, n)


def run_distribution_analysis(metric_column: str, bins: int = 10):
    """Analyze the distribution of a metric."""
    data = load_anime_data()
    return analyze_metric_distribution(data, metric_column, bins)
