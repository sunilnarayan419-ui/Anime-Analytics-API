"""Supported metrics and shared numeric helpers.

The registry below is the single list of columns the API exposes for
analysis. Analytical functions themselves work on any numeric DataFrame
column; the API layer restricts requests to these metrics so arbitrary column
names cannot reach the analytics code.
"""

from dataclasses import dataclass
from numbers import Integral
from typing import Literal

import numpy as np
import pandas as pd

from anime_analytics.exceptions import AnalysisError

MetricKind = Literal["count", "score", "rank"]

# Literal types are written out so FastAPI publishes them as enums in the
# OpenAPI schema and mypy can check them. tests/test_analytics.py verifies
# that they stay in sync with the registry below.
MetricName = Literal[
    "Score",
    "Episodes",
    "Ranked",
    "Popularity",
    "Members",
    "Favorites",
    "Watching",
    "Completed",
    "On-Hold",
    "Dropped",
    "Plan to Watch",
    "Score-10",
    "Score-9",
    "Score-8",
    "Score-7",
    "Score-6",
    "Score-5",
    "Score-4",
    "Score-3",
    "Score-2",
    "Score-1",
]

CountMetricName = Literal[
    "Episodes",
    "Members",
    "Favorites",
    "Watching",
    "Completed",
    "On-Hold",
    "Dropped",
    "Plan to Watch",
    "Score-10",
    "Score-9",
    "Score-8",
    "Score-7",
    "Score-6",
    "Score-5",
    "Score-4",
    "Score-3",
    "Score-2",
    "Score-1",
]


@dataclass(frozen=True)
class MetricInfo:
    """Description of one analysable column.

    Kinds:
        count: additive, non-negative quantity (sums and shares are meaningful).
        score: an average rating (means are meaningful, sums are not).
        rank: a position where a *lower* number is better (sums are meaningless).
    """

    name: str
    kind: MetricKind
    description: str


def _score_votes() -> list[MetricInfo]:
    return [
        MetricInfo(f"Score-{n}", "count", f"Number of users who scored {n}")
        for n in range(10, 0, -1)
    ]


METRICS: dict[str, MetricInfo] = {
    info.name: info
    for info in [
        MetricInfo("Score", "score", "Average user score (0-10)"),
        MetricInfo("Episodes", "count", "Number of episodes"),
        MetricInfo("Ranked", "rank", "Rank by score (1 is best)"),
        MetricInfo("Popularity", "rank", "Rank by list additions (1 is most popular)"),
        MetricInfo("Members", "count", "Users who added the title to their list"),
        MetricInfo("Favorites", "count", "Users who marked the title as a favorite"),
        MetricInfo("Watching", "count", "Users currently watching"),
        MetricInfo("Completed", "count", "Users who completed it"),
        MetricInfo("On-Hold", "count", "Users who put it on hold"),
        MetricInfo("Dropped", "count", "Users who dropped it"),
        MetricInfo("Plan to Watch", "count", "Users who plan to watch it"),
        *_score_votes(),
    ]
}


def get_metric(name: str) -> MetricInfo:
    """Return the registry entry for ``name`` or raise ``AnalysisError``."""
    try:
        return METRICS[name]
    except KeyError:
        raise AnalysisError(f"Unsupported metric: {name}") from None


def validate_positive_int(value: object, name: str) -> int:
    """Return ``value`` as an ``int`` if it is a positive integer.

    Booleans, floats and strings are rejected on purpose: ``True`` would
    otherwise pass as ``1`` and ``2.0`` would hide a caller mistake.
    """
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise AnalysisError(f"{name} must be a positive integer")
    return int(value)


def numeric_series(data: pd.DataFrame, column: str) -> pd.Series:
    """Return ``data[column]`` as ``float64`` with invalid values set to NaN.

    Non-numeric entries (for example the text ``"Unknown"``) and infinite
    values become NaN. Nothing is imputed: callers decide how to treat NaN.
    The result keeps the index of ``data``; the input is never modified.
    """
    if column not in data.columns:
        raise AnalysisError(f"Unknown metric column: {column}")

    parsed = pd.to_numeric(data[column], errors="coerce")
    array = parsed.to_numpy(dtype="float64", na_value=np.nan, copy=True)
    array[~np.isfinite(array)] = np.nan
    return pd.Series(array, index=data.index, name=column)
