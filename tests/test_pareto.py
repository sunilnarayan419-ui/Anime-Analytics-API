import pytest

from anime_analytics.analytics.pareto import calculate_pareto


def test_pareto_proportions_sum_to_one(sample_anime_data):
    result = calculate_pareto(sample_anime_data, "Completed", n=5)

    assert len(result) == 5
    assert abs(result.sum() - 1.0) < 1e-9
    assert result.index.tolist() == [
        "Group 1", "Group 2", "Group 3", "Group 4", "Group 5"
    ]


def test_invalid_group_count_is_rejected(sample_anime_data):
    with pytest.raises(ValueError):
        calculate_pareto(sample_anime_data, "Completed", n=0)


def test_zero_total_is_rejected(sample_anime_data):
    sample_anime_data["Completed"] = 0

    with pytest.raises(ValueError):
        calculate_pareto(sample_anime_data, "Completed", n=5)
