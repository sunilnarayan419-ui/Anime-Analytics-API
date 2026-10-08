import pytest

from anime_analytics.analytics.descriptive import describe_metric


def test_descriptive_statistics(sample_anime_data):
    result = describe_metric(sample_anime_data, "Completed")

    assert result["count"] == 5
    assert result["median"] == 60


def test_unknown_metric_is_rejected(sample_anime_data):
    with pytest.raises(ValueError):
        describe_metric(sample_anime_data, "Unknown")
