import pandas as pd
import pytest

from anime_analytics.exceptions import AnalysisError, DatasetError
from anime_analytics.repositories.anime_repository import AnimeRepository


def ids(page: pd.DataFrame) -> list[int]:
    return page["MAL_ID"].tolist()


# --- loading -----------------------------


def test_from_csv_loads_and_cleans(tmp_path, raw_anime):
    path = tmp_path / "anime.csv"
    raw_anime.to_csv(path, index=False)

    repository = AnimeRepository.from_csv(path)

    assert len(repository) == 7
    assert repository.report.rows_raw == 7
    assert pd.isna(repository.data.loc[repository.data["MAL_ID"] == 3, "Score"]).all()


def test_from_csv_keeps_literal_na_text_for_the_cleaner(tmp_path, raw_anime):
    raw_anime.loc[0, "Name"] = "NA"  # a real title must not turn into NaN
    path = tmp_path / "anime.csv"
    raw_anime.to_csv(path, index=False)

    repository = AnimeRepository.from_csv(path)

    assert repository.get_by_id(1)["Name"] == "NA"


def test_from_csv_missing_file(tmp_path):
    with pytest.raises(DatasetError, match="not found"):
        AnimeRepository.from_csv(tmp_path / "missing.csv")


def test_from_csv_empty_file(tmp_path):
    path = tmp_path / "anime.csv"
    path.write_text("")

    with pytest.raises(DatasetError, match="could not be parsed"):
        AnimeRepository.from_csv(path)


def test_from_csv_wrong_columns(tmp_path):
    path = tmp_path / "anime.csv"
    path.write_text("a,b\n1,2\n")

    with pytest.raises(DatasetError, match="Missing required columns"):
        AnimeRepository.from_csv(path)


def test_from_csv_rejects_non_utf8(tmp_path):
    path = tmp_path / "anime.csv"
    path.write_bytes(b"MAL_ID,Name\n1,\xff\xfe\n")

    with pytest.raises(DatasetError):
        AnimeRepository.from_csv(path)


# --- lookup -----------------------------


def test_get_by_id_returns_python_values_and_none_for_missing(repository):
    record = repository.get_by_id(3)

    assert record["Name"] == "Gamma"
    assert record["Score"] is None
    assert record["Episodes"] is None
    assert record["Members"] == 600
    assert type(record["Members"]) is int
    assert type(record["MAL_ID"]) is int


def test_get_by_id_unknown(repository):
    assert repository.get_by_id(12345) is None


# --- query -----------------------------


def test_default_query_is_ordered_by_id(repository):
    total, page = repository.query()

    assert total == 7
    assert ids(page) == [1, 2, 3, 4, 5, 6, 7]


def test_pagination(repository):
    total, page = repository.query(limit=3, offset=2)
    assert (total, ids(page)) == (7, [3, 4, 5])

    total, page = repository.query(limit=3, offset=6)
    assert (total, ids(page)) == (7, [7])

    total, page = repository.query(limit=3, offset=50)
    assert (total, ids(page)) == (7, [])


def test_filter_by_type_is_case_insensitive(repository):
    assert ids(repository.query(anime_type="tv")[1]) == [1, 3, 5]
    assert ids(repository.query(anime_type=" Movie ")[1]) == [2]
    assert repository.query(anime_type="Nothing")[0] == 0


def test_filter_by_genre_matches_whole_genre_only(repository):
    assert ids(repository.query(genre="action")[1]) == [1, 2, 5]
    assert ids(repository.query(genre="Comedy")[1]) == [1, 3, 7]
    assert repository.query(genre="act")[0] == 0
    assert repository.query(genre="Unknown")[0] == 0


def test_genre_filter_escapes_regex_characters(repository):
    assert repository.query(genre="Sci-Fi.*")[0] == 0
    assert repository.query(genre="(")[0] == 0


def test_filter_by_name_searches_title_and_english_title(repository):
    assert ids(repository.query(name="force")[1]) == [4]
    assert ids(repository.query(name="SECOND")[1]) == [2]  # English name
    assert repository.query(name="Unknown")[0] == 0  # placeholder is not text


def test_filter_by_score_range_excludes_unscored_titles(repository):
    assert ids(repository.query(min_score=7)[1]) == [1, 2, 5]
    assert ids(repository.query(max_score=6)[1]) == [4, 7]
    assert ids(repository.query(min_score=6, max_score=8.5)[1]) == [1, 2, 4]


def test_filters_combine_with_and(repository):
    total, page = repository.query(anime_type="TV", genre="Drama")

    assert (total, ids(page)) == (2, [3, 5])


def test_sort_descending_puts_missing_values_last(repository):
    _, page = repository.query(sort_by="Score", ascending=False)

    assert ids(page) == [5, 1, 2, 4, 7, 3, 6]


def test_sort_ascending_puts_missing_values_last(repository):
    _, page = repository.query(sort_by="Score", ascending=True)

    assert ids(page) == [7, 4, 2, 1, 5, 3, 6]


def test_sort_ties_keep_original_order(repository):
    _, page = repository.query(sort_by="Members", ascending=False)

    assert ids(page) == [1, 2, 3, 4, 5, 6, 7]


def test_sort_by_name(repository):
    _, page = repository.query(sort_by="Name")

    assert page["Name"].tolist() == [
        "Alpha", "Beta", "Delta Force", "Epsilon", "Eta", "Gamma", "Zeta",
    ]  # fmt: skip


def test_sort_by_unsupported_column_is_rejected(repository):
    with pytest.raises(AnalysisError, match="Cannot sort"):
        repository.query(sort_by="Genres")


def test_query_does_not_change_stored_data(repository):
    before = repository.data.copy(deep=True)

    repository.query(anime_type="TV", sort_by="Members", ascending=False, limit=2)

    pd.testing.assert_frame_equal(repository.data, before)
