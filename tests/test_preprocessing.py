from anime_analytics.analytics.preprocessing import preprocess_anime


def test_preprocess_removes_duplicate_ids(sample_anime_data):
    data = sample_anime_data.copy()
    data = __import__("pandas").concat([data, data.iloc[[0]]])

    result = preprocess_anime(data)

    assert result["MAL_ID"].is_unique
    assert len(result) == 5
