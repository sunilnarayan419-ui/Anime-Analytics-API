# Data Dictionary

Source: `anime.csv`, MyAnimeList Database 2020
(<https://github.com/Hernan4444/MyAnimelist-Database>). The file has 17,562 rows
and 35 columns. Counts below describe the version checked while building this
project; a different copy of the file may differ.

The CSV is read with every value as text. The preprocessing step
(`analytics/preprocessing.py`) then assigns the types below. `Unknown` and
empty text always become a missing value (`NaN` / `<NA>` internally,
`null` in JSON).

## Columns used by the API

| Column | Stored as | Meaning | Missing in checked file |
|---|---|---|---|
| `MAL_ID` | int | MyAnimeList identifier, unique key | 0 |
| `Name` | text | Title | 0 |
| `Score` | float | Average user score, valid range 0–10 | 5,141 |
| `Genres` | text | Comma-separated genre list (returned as a list by the API) | 63 |
| `English name`, `Japanese name` | text | Alternative titles | many |
| `Type` | text | TV, Movie, OVA, Special, ONA, Music | 37 |
| `Episodes` | Int64 | Episode count | 516 |
| `Aired`, `Premiered`, `Producers`, `Licensors`, `Studios`, `Source`, `Duration`, `Rating` | text | Descriptive metadata | varies |
| `Ranked` | Int64 | Rank by score, **1 is best** | 1,762 (+2 invalid zeros) |
| `Popularity` | Int64 | Rank by list additions, **1 is most popular** | 2 invalid zeros |
| `Members` | Int64 | Users who added the title to their list | 0 |
| `Favorites` | Int64 | Users who marked it a favorite | 0 |
| `Watching`, `Completed`, `On-Hold`, `Dropped`, `Plan to Watch` | Int64 | Users per list status | 0 |
| `Score-10` … `Score-1` | Int64 | Users who gave that score | many (titles with no score) |

## Metric kinds

The API restricts analysis to these columns and treats them differently:

| Kind | Columns | Rules |
|---|---|---|
| `count` | Episodes, Members, Favorites, Watching, Completed, On-Hold, Dropped, Plan to Watch, Score-1 … Score-10 | Additive: sums, shares and Pareto analysis are meaningful. |
| `score` | Score | An average: means and medians are meaningful, **sums are not** (reported as `null`). |
| `rank` | Ranked, Popularity | A position: lower is better; sums and means are not meaningful. |

`Episodes` is a count but a poor Pareto candidate in practice, because one title can be
a very long-running series; it is allowed because the maths is valid.

## Derived engagement metrics

Computed per anime in `analytics/engagement.py` (never stored in the dataset):

| Metric | Definition |
|---|---|
| `list_total` | Watching + Completed + On-Hold + Dropped + Plan to Watch |
| `completion_rate` | Completed / list_total |
| `drop_rate` | Dropped / list_total |
| `favorite_rate` | Favorites / Members |

A rate is missing whenever an input is missing or the denominator is zero.

## Known data quirks

- **Placeholder zeros in rank columns.** Two titles have `Popularity` and
  `Ranked` equal to 0 (and 1 member). Rank columns start at 1, so these are
  treated as missing.
- **`Score` is missing for 29% of titles** (unrated or too few ratings). They
  are excluded from score statistics, not treated as 0.
- **`Type` is `Unknown` for 37 titles.** Type comparisons group them under
  `"Unknown"`; the record itself reports `type: null`.
- **`Popularity`/`Ranked` are not dense.** The highest `Popularity` value is
  larger than the number of rows, so gaps exist.
- **Snapshot data.** Values reflect the 2020/early-2021 scrape, not live
  MyAnimeList numbers.
