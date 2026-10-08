from anime_analytics.analytics.pareto import calculate_pareto
from anime_analytics.repositories.anime_repository import load_anime_data


def run_pareto_analysis(metric_column: str, n: int):
    data = load_anime_data()
    return calculate_pareto(data, metric_column, n)
