import pandas as pd
import pytest

from anime_analytics.analytics.preprocessing import (
    REQUIRED_COLUMNS,
    preprocess_anime,
)
from anime_analytics.exceptions import DatasetError


def test_missing_required_columns_are_reported(raw_anime):
    broken = raw_anime.drop(columns=["Members", "Type"])

    with pytest.raises(DatasetError) as error:
        preprocess_anime(broken)

    assert "Members" in str(error.value)
    assert "Type" in str(error.value)


def test_dataset_error_is_a_value_error(raw_anime):
    with pytest.raises(ValueError):
        preprocess_anime(raw_anime.drop(columns=["MAL_ID"]))


def test_required_columns_exist_in_fixture(raw_anime):
    assert set(raw_anime.columns) >= REQUIRED_COLUMNS


def test_duplicate_ids_keep_first_occurrence(raw_anime):
    duplicate = raw_anime.iloc[[0]].copy()
    duplicate["Name"] = "Impostor"
    raw = pd.concat([raw_anime, duplicate], ignore_index=True)

    result = preprocess_anime(raw)

    assert result.data["MAL_ID"].is_unique
    assert len(result.data) == 7
    assert result.data.loc[result.data["MAL_ID"] == 1, "Name"].item() == "Alpha"
    assert result.report.duplicate_ids_removed == 1
    assert result.report.rows_raw == 8
    assert result.report.rows_clean == 7


@pytest.mark.parametrize("bad_id", ["", "abc", "Unknown", "0", "-4", "1.5"])
def test_invalid_ids_are_dropped_and_counted(raw_anime, bad_id):
    raw_anime.loc[0, "MAL_ID"] = bad_id

    result = preprocess_anime(raw_anime)

    assert len(result.data) == 6
    assert result.report.invalid_id_rows_removed == 1


def test_unknown_and_blank_text_become_missing(raw_anime):
    raw_anime.loc[0, "Type"] = "  "
    result = preprocess_anime(raw_anime).data

    assert pd.isna(result.loc[result["MAL_ID"] == 6, "Type"].item())  # "Unknown"
    assert pd.isna(result.loc[result["MAL_ID"] == 1, "Type"].item())  # blank
    assert result.loc[result["MAL_ID"] == 2, "Type"].item() == "Movie"


def test_text_is_trimmed(raw_anime):
    raw_anime.loc[0, "Name"] = "  Alpha  "

    result = preprocess_anime(raw_anime).data

    assert result.loc[0, "Name"] == "Alpha"


def test_numeric_columns_get_numeric_dtypes_and_nan_for_unknown(clean_anime):
    assert str(clean_anime["MAL_ID"].dtype) == "int64"
    assert str(clean_anime["Score"].dtype) == "float64"
    assert str(clean_anime["Members"].dtype) == "Int64"
    assert str(clean_anime["Episodes"].dtype) == "Int64"
    assert clean_anime["Score"].isna().sum() == 2
    assert clean_anime["Episodes"].isna().sum() == 1
    assert clean_anime["Members"].tolist() == [1000, 800, 600, 400, 200, 100, 100]


def test_missing_values_are_not_invented(clean_anime):
    gamma = clean_anime.loc[clean_anime["MAL_ID"] == 3].iloc[0]

    assert pd.isna(gamma["Score"])
    assert pd.isna(gamma["Episodes"])


def test_invalid_numbers_are_set_missing_and_reported(raw_anime):
    raw_anime.loc[0, "Members"] = "lots"  # unparseable
    raw_anime.loc[1, "Favorites"] = "-5"  # negative count
    raw_anime.loc[3, "Score"] = "11.5"  # outside 0-10
    raw_anime.loc[4, "Completed"] = "inf"  # not finite

    result = preprocess_anime(raw_anime)
    data = result.data

    assert pd.isna(data.loc[0, "Members"])
    assert pd.isna(data.loc[1, "Favorites"])
    assert pd.isna(data.loc[3, "Score"])
    assert pd.isna(data.loc[4, "Completed"])
    assert result.report.invalid_values_set_missing["Members"] == 1
    assert result.report.invalid_values_set_missing["Favorites"] == 1
    assert result.report.invalid_values_set_missing["Score"] == 1


def test_unknown_placeholder_is_not_counted_as_invalid(clean_anime, raw_anime):
    report = preprocess_anime(raw_anime).report

    assert report.invalid_values_set_missing == {}


def test_rank_columns_below_one_are_missing(raw_anime):
    raw_anime.loc[0, "Popularity"] = "0"
    raw_anime.loc[1, "Ranked"] = "0.0"

    result = preprocess_anime(raw_anime)

    assert pd.isna(result.data.loc[0, "Popularity"])
    assert result.report.invalid_values_set_missing["Popularity"] == 1


def test_non_integral_count_keeps_decimals(raw_anime):
    raw_anime.loc[0, "Members"] = "10.5"

    data = preprocess_anime(raw_anime).data

    assert data.loc[0, "Members"] == 10.5


def test_source_data_is_not_mutated(raw_anime):
    before = raw_anime.copy(deep=True)

    preprocess_anime(raw_anime)

    pd.testing.assert_frame_equal(raw_anime, before)


def test_optional_columns_may_be_absent(raw_anime):
    slim = raw_anime.drop(columns=["English name"])

    assert "English name" not in preprocess_anime(slim).data.columns


def test_empty_table_with_columns_is_accepted(raw_anime):
    result = preprocess_anime(raw_anime.iloc[0:0])

    assert result.data.empty
    assert result.report.rows_clean == 0
