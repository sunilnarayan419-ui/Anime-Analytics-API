import numpy as np
import pandas as pd
import pytest

from anime_analytics.analytics.pareto import calculate_pareto
from anime_analytics.exceptions import AnalysisError


def frame(values, column="Completed"):
    return pd.DataFrame({"MAL_ID": range(1, len(values) + 1), column: values})


def test_one_value_per_group():
    result = calculate_pareto(frame([100, 80, 60, 40, 20]), "Completed", n=5)

    assert result.index.tolist() == [f"Group {i}" for i in range(1, 6)]
    np.testing.assert_allclose(result.to_numpy(), np.array([100, 80, 60, 40, 20]) / 300)
    assert result.sum() == pytest.approx(1.0)


def test_returns_series_of_floats_named_after_metric():
    result = calculate_pareto(frame([3, 2, 1]), "Completed", n=3)

    assert isinstance(result, pd.Series)
    assert result.dtype == "float64"
    assert result.name == "Completed"


def test_unequal_group_sizes_are_handled():
    # 10 observations in 3 groups -> sizes 4, 3, 3 -> (10+9+8+7), (6+5+4), (3+2+1)
    result = calculate_pareto(frame(range(1, 11)), "Completed", n=3)

    np.testing.assert_allclose(result.to_numpy(), np.array([34, 15, 6]) / 55)


def test_seven_observations_in_five_groups():
    result = calculate_pareto(frame([500, 400, 300, 200, 100, 50, 50]), "Completed", 5)

    # Group sizes are 2, 1, 1, 1, 2.
    np.testing.assert_allclose(
        result.to_numpy(), np.array([900, 300, 200, 100, 100]) / 1600
    )


def test_groups_are_sorted_by_proportion_descending():
    result = calculate_pareto(frame([1, 50, 7, 300, 4, 9, 20, 2]), "Completed", n=4)

    assert result.is_monotonic_decreasing
    assert result.sum() == pytest.approx(1.0)


def test_input_order_does_not_change_result():
    values = [5, 90, 3, 1, 1, 40, 7, 12, 8, 2]
    shuffled = list(np.random.default_rng(0).permutation(values))

    pd.testing.assert_series_equal(
        calculate_pareto(frame(values), "Completed", 5),
        calculate_pareto(frame(shuffled), "Completed", 5),
    )


def test_concentrated_metric_is_reported_as_concentrated():
    result = calculate_pareto(frame([90, 5, 3, 1, 1]), "Completed", n=5)

    assert result["Group 1"] == pytest.approx(0.90)
    assert result["Group 2"] == pytest.approx(0.05)


def test_equal_values_split_evenly():
    result = calculate_pareto(frame([10, 10, 10, 10, 10]), "Completed", n=5)

    np.testing.assert_allclose(result.to_numpy(), [0.2] * 5)


def test_ties_still_form_the_requested_number_of_groups():
    # rank(method="first") gives tied values distinct ranks, so qcut never
    # sees duplicate bin edges.
    result = calculate_pareto(frame([5, 5, 5, 1]), "Completed", n=2)

    np.testing.assert_allclose(result.to_numpy(), [10 / 16, 6 / 16])
    assert len(result) == 2


def test_single_group_holds_everything():
    result = calculate_pareto(frame([4, 3, 2]), "Completed", n=1)

    assert result.tolist() == [1.0]
    assert result.index.tolist() == ["Group 1"]


def test_group_count_equal_to_observations_is_allowed():
    assert len(calculate_pareto(frame([3, 2, 1]), "Completed", n=3)) == 3


def test_numpy_integer_group_count_is_accepted():
    assert len(calculate_pareto(frame([3, 2, 1, 1]), "Completed", n=np.int64(2))) == 2


@pytest.mark.parametrize("n", [0, -1, -10, 1.5, 2.0, "3", None, True])
def test_invalid_group_count_is_rejected(n):
    with pytest.raises(AnalysisError, match="positive integer"):
        calculate_pareto(frame([3, 2, 1]), "Completed", n=n)


def test_more_groups_than_observations_is_rejected():
    with pytest.raises(AnalysisError, match="Cannot form 4 groups from 3"):
        calculate_pareto(frame([3, 2, 1]), "Completed", n=4)


def test_unknown_metric_is_rejected():
    with pytest.raises(AnalysisError, match="Unknown metric column"):
        calculate_pareto(frame([3, 2, 1]), "Nope", n=2)


def test_missing_and_non_numeric_values_are_excluded_not_zeroed():
    data = frame([100, None, "Unknown", 50, "abc", 50])

    result = calculate_pareto(data, "Completed", n=3)

    # Only 100, 50, 50 are valid -> three groups of one observation.
    np.testing.assert_allclose(result.to_numpy(), [0.5, 0.25, 0.25])


def test_too_many_groups_after_dropping_missing_values():
    with pytest.raises(AnalysisError, match="Cannot form 3 groups from 2"):
        calculate_pareto(frame([5, None, None, 1]), "Completed", n=3)


def test_infinite_values_are_treated_as_invalid():
    result = calculate_pareto(frame([4, float("inf"), 1]), "Completed", n=2)

    np.testing.assert_allclose(result.to_numpy(), [0.8, 0.2])


def test_column_without_any_numeric_value_is_rejected():
    with pytest.raises(AnalysisError, match="No valid numeric values"):
        calculate_pareto(frame(["a", "b", None]), "Completed", n=2)


def test_negative_values_are_rejected():
    with pytest.raises(AnalysisError, match="non-negative"):
        calculate_pareto(frame([10, -1, 5]), "Completed", n=2)


def test_zero_total_is_rejected():
    with pytest.raises(AnalysisError, match="positive"):
        calculate_pareto(frame([0, 0, 0, 0]), "Completed", n=2)


def test_empty_dataset_is_rejected():
    with pytest.raises(AnalysisError, match="empty"):
        calculate_pareto(frame([]), "Completed", n=2)


def test_empty_frame_without_the_column_reports_unknown_metric():
    with pytest.raises(AnalysisError, match="Unknown metric column"):
        calculate_pareto(pd.DataFrame(), "Completed", n=2)


def test_input_is_not_modified():
    data = frame([5, 3, 1, 7])
    before = data.copy(deep=True)

    calculate_pareto(data, "Completed", n=2)

    pd.testing.assert_frame_equal(data, before)


def test_duplicate_index_labels_do_not_break_grouping():
    data = pd.DataFrame({"Completed": [8, 6, 4, 2]}, index=[0, 0, 1, 1])

    result = calculate_pareto(data, "Completed", n=2)

    np.testing.assert_allclose(result.to_numpy(), [14 / 20, 6 / 20])


def test_nullable_integer_column_is_supported():
    data = pd.DataFrame({"Completed": pd.array([10, None, 5, 5], dtype="Int64")})

    result = calculate_pareto(data, "Completed", n=3)

    np.testing.assert_allclose(result.to_numpy(), [0.5, 0.25, 0.25])


def test_real_world_shape_sums_to_one(clean_anime):
    result = calculate_pareto(clean_anime, "Members", n=3)

    assert result.sum() == pytest.approx(1.0)
    assert len(result) == 3
