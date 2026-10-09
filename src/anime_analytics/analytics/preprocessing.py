"""Validation and cleaning of the raw MyAnimeList ``anime.csv`` data.

The cleaning rules are documented in ``docs/analytical_methodology.md``. In
short: nothing is imputed or invented. Placeholders such as ``"Unknown"``
become missing values, impossible values become missing values, and every
such decision is counted in the returned :class:`PreprocessingReport`.
"""

from dataclasses import dataclass, field

import pandas as pd

from anime_analytics.exceptions import DatasetError

# Columns the application cannot work without.
REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {
        "MAL_ID",
        "Name",
        "Score",
        "Genres",
        "Type",
        "Episodes",
        "Popularity",
        "Members",
        "Favorites",
        "Watching",
        "Completed",
        "On-Hold",
        "Dropped",
        "Plan to Watch",
    }
)

# Columns holding whole numbers (stored as nullable Int64 when integral).
INTEGER_COLUMNS: tuple[str, ...] = (
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
    *(f"Score-{n}" for n in range(10, 0, -1)),
)

# Rank columns start at 1; the source data contains a few 0 placeholders.
RANK_COLUMNS: frozenset[str] = frozenset({"Ranked", "Popularity"})

# Average score, valid between 0 and 10 inclusive.
SCORE_COLUMN = "Score"
SCORE_RANGE = (0.0, 10.0)

TEXT_COLUMNS: tuple[str, ...] = (
    "Name",
    "Genres",
    "English name",
    "Japanese name",
    "Type",
    "Aired",
    "Premiered",
    "Producers",
    "Licensors",
    "Studios",
    "Source",
    "Duration",
    "Rating",
)

# Case-insensitive text values that mean "no value".
MISSING_TOKENS: frozenset[str] = frozenset({"", "unknown"})


@dataclass(frozen=True)
class PreprocessingReport:
    """What the cleaning step changed, for transparency and testing."""

    rows_raw: int
    rows_clean: int
    invalid_id_rows_removed: int
    duplicate_ids_removed: int
    invalid_values_set_missing: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class PreprocessResult:
    """Cleaned data together with the report describing the cleaning."""

    data: pd.DataFrame
    report: PreprocessingReport


def _clean_text(series: pd.Series) -> pd.Series:
    """Trim whitespace and turn empty/"Unknown" text into missing values."""
    text = series.astype("string").str.strip()
    is_missing = text.isna() | text.str.lower().isin(MISSING_TOKENS)
    return text.mask(is_missing)


def _clean_numeric(series: pd.Series) -> tuple[pd.Series, int]:
    """Parse a column to numbers.

    Returns the parsed float series (unparseable entries are NaN) and the
    number of entries that were real values but could not be parsed. Entries
    that were already missing or the "Unknown" placeholder are not counted.
    """
    parsed = pd.to_numeric(series, errors="coerce").astype("float64")
    as_text = series.astype("string").str.strip().str.lower()
    was_missing = as_text.isna() | as_text.isin(MISSING_TOKENS)
    unparseable = int((parsed.isna() & ~was_missing).sum())
    return parsed, unparseable


def _finalize_integer(parsed: pd.Series) -> pd.Series:
    """Store integral values as nullable ``Int64``; otherwise keep ``float64``."""
    present = parsed.dropna()
    if bool((present % 1 == 0).all()):
        return parsed.astype("Int64")
    return parsed


def preprocess_anime(raw: pd.DataFrame) -> PreprocessResult:
    """Validate and clean the raw anime table.

    Steps:
        1. Check that all required columns exist.
        2. Trim text and convert "Unknown"/empty text to missing values.
        3. Drop rows whose ``MAL_ID`` is missing or not a positive integer.
        4. Drop repeated ``MAL_ID`` rows, keeping the first occurrence.
        5. Parse numeric columns. Unparseable, infinite, negative (counts),
           below 1 (``Ranked``/``Popularity``) or out-of-range (score) values
           become missing.
        6. Use nullable ``Int64`` for whole-number columns.

    The input frame is never modified.

    Raises:
        DatasetError: If required columns are missing.
    """
    missing_columns = sorted(REQUIRED_COLUMNS - set(raw.columns))
    if missing_columns:
        raise DatasetError(f"Missing required columns: {missing_columns}")

    data = raw.copy()

    for column in TEXT_COLUMNS:
        if column in data.columns:
            data[column] = _clean_text(data[column])

    ids = pd.to_numeric(data["MAL_ID"], errors="coerce")
    valid_id = ids.notna() & (ids > 0) & (ids % 1 == 0)
    invalid_id_rows = int((~valid_id).sum())
    data = data.loc[valid_id].copy()
    data["MAL_ID"] = ids.loc[valid_id].astype("int64")

    is_duplicate = data["MAL_ID"].duplicated(keep="first")
    duplicate_ids = int(is_duplicate.sum())
    data = data.loc[~is_duplicate].reset_index(drop=True)

    invalid_values: dict[str, int] = {}

    def record_invalid(column: str, count: int) -> None:
        if count:
            invalid_values[column] = invalid_values.get(column, 0) + count

    for column in INTEGER_COLUMNS:
        if column not in data.columns:
            continue
        parsed, unparseable = _clean_numeric(data[column])
        minimum = 1 if column in RANK_COLUMNS else 0
        too_small = parsed < minimum
        record_invalid(column, unparseable + int(too_small.sum()))
        parsed = parsed.mask(too_small | ~parsed.abs().lt(float("inf")))
        data[column] = _finalize_integer(parsed)

    parsed, unparseable = _clean_numeric(data[SCORE_COLUMN])
    low, high = SCORE_RANGE
    out_of_range = (parsed < low) | (parsed > high)
    record_invalid(SCORE_COLUMN, unparseable + int(out_of_range.sum()))
    data[SCORE_COLUMN] = parsed.mask(out_of_range | ~parsed.abs().lt(float("inf")))

    report = PreprocessingReport(
        rows_raw=len(raw),
        rows_clean=len(data),
        invalid_id_rows_removed=invalid_id_rows,
        duplicate_ids_removed=duplicate_ids,
        invalid_values_set_missing=invalid_values,
    )
    return PreprocessResult(data=data, report=report)
