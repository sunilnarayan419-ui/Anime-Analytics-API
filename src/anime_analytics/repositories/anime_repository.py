"""Data access for the anime dataset.

The CSV is read and cleaned **once** when a repository is created; requests
only read from the cleaned in-memory table. The raw table is not kept.
"""

import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from anime_analytics.analytics.preprocessing import (
    PreprocessingReport,
    preprocess_anime,
)
from anime_analytics.exceptions import AnalysisError, DatasetError

logger = logging.getLogger(__name__)

SORTABLE_COLUMNS: tuple[str, ...] = (
    "MAL_ID",
    "Name",
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
)


def _as_bool(mask: pd.Series) -> pd.Series:
    """Treat missing comparison results as ``False``."""
    return mask.fillna(False).astype(bool)


def to_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert rows to dictionaries, turning every missing value into ``None``."""
    cleaned = frame.astype(object).where(frame.notna(), None)
    return [{str(k): v for k, v in row.items()} for row in cleaned.to_dict("records")]


class AnimeRepository:
    """Read-only access to the cleaned anime table.

    The table returned by :attr:`data` is shared between requests and must be
    treated as read-only; all analytical functions copy before changing.
    """

    def __init__(self, data: pd.DataFrame, report: PreprocessingReport) -> None:
        self._data = data
        self._report = report
        self._positions = pd.Series(
            np.arange(len(data)), index=data["MAL_ID"].to_numpy()
        )

    @classmethod
    def from_dataframe(cls, raw: pd.DataFrame) -> "AnimeRepository":
        """Build a repository from a raw (uncleaned) DataFrame."""
        result = preprocess_anime(raw)
        return cls(result.data, result.report)

    @classmethod
    def from_csv(cls, path: Path) -> "AnimeRepository":
        """Read ``anime.csv`` from ``path`` and clean it.

        Everything is read as text so the preprocessing step, not the CSV
        parser, decides what each value means.

        Raises:
            DatasetError: If the file is missing, empty, unreadable or does
                not contain the required columns.
        """
        path = Path(path)
        if not path.is_file():
            raise DatasetError(f"Dataset file not found: {path}")
        try:
            raw = pd.read_csv(path, dtype=str, keep_default_na=False)
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
            raise DatasetError(f"Dataset file could not be parsed: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise DatasetError("Dataset file is not valid UTF-8 text") from exc

        repository = cls.from_dataframe(raw)
        report = repository.report
        logger.info(
            "Loaded %d anime from %s (%d duplicate ids and %d invalid ids removed)",
            report.rows_clean,
            path,
            report.duplicate_ids_removed,
            report.invalid_id_rows_removed,
        )
        return repository

    @property
    def data(self) -> pd.DataFrame:
        """The cleaned table (shared; do not modify)."""
        return self._data

    @property
    def report(self) -> PreprocessingReport:
        return self._report

    def __len__(self) -> int:
        return len(self._data)

    def get_by_id(self, mal_id: int) -> dict[str, Any] | None:
        """Return one anime record, or ``None`` if the id is unknown."""
        position = self._positions.get(mal_id)
        if position is None:
            return None
        return to_records(self._data.iloc[[int(position)]])[0]

    def query(
        self,
        *,
        anime_type: str | None = None,
        genre: str | None = None,
        name: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        sort_by: str = "MAL_ID",
        ascending: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, pd.DataFrame]:
        """Filter, sort and paginate the table.

        Filters are combined with AND:

        * ``anime_type``: exact match, case-insensitive.
        * ``genre``: exact genre name, case-insensitive (``"action"`` does not
          match ``"Action Adventure"``-style partial names).
        * ``name``: case-insensitive substring of the title or English title.
        * ``min_score`` / ``max_score``: inclusive bounds; anime without a
          score never match a score filter.

        Missing values in the sort column are always placed last. Ties keep
        the original row order, so pages are stable.

        Returns:
            ``(total, page)`` where ``total`` is the number of rows matching
            the filters before pagination.
        """
        if sort_by not in SORTABLE_COLUMNS:
            raise AnalysisError(f"Cannot sort by: {sort_by}")

        data = self._data
        mask = pd.Series(True, index=data.index)

        if anime_type:
            mask &= _as_bool(data["Type"].str.lower() == anime_type.strip().lower())

        if genre:
            pattern = rf"(?:^|,)\s*{re.escape(genre.strip().lower())}\s*(?:,|$)"
            mask &= _as_bool(data["Genres"].str.lower().str.contains(pattern))

        if name:
            needle = name.strip()
            hit = data["Name"].str.contains(needle, case=False, regex=False)
            if "English name" in data.columns:
                hit = hit | data["English name"].str.contains(
                    needle, case=False, regex=False
                )
            mask &= _as_bool(hit)

        if min_score is not None:
            mask &= data["Score"] >= min_score
        if max_score is not None:
            mask &= data["Score"] <= max_score

        filtered = data.loc[mask].sort_values(
            sort_by, ascending=ascending, na_position="last", kind="mergesort"
        )
        return len(filtered), filtered.iloc[offset : offset + limit]
