# Analytical Methodology

This document defines what each analysis computes and the assumptions behind
it. Code lives in `src/anime_analytics/analytics/`; none of it depends on HTTP.

## 1. Cleaning rules (`preprocessing.py`)

Applied once, at load time, to a copy of the raw table:

1. **Required columns** (`MAL_ID`, `Name`, `Score`, `Genres`, `Type`,
   `Episodes`, `Popularity`, `Members`, `Favorites`, `Watching`, `Completed`,
   `On-Hold`, `Dropped`, `Plan to Watch`) must exist, otherwise `DatasetError`.
2. **Text**: whitespace is trimmed; empty text and `Unknown` (any case)
   become missing.
3. **Identifiers**: rows whose `MAL_ID` is missing, non-numeric, non-integral
   or below 1 are removed and counted.
4. **Duplicates**: repeated `MAL_ID` rows are removed, **keeping the first**,
   and counted.
5. **Numbers**: unparseable and infinite values become missing; counts below
   0, rank columns below 1, and `Score` outside 0–10 become missing. Each such
   change is counted per column (`invalid_values_set_missing`). The `Unknown`
   placeholder is *not* counted as invalid.
6. **Types**: whole-number columns use pandas nullable `Int64` (kept as float
   only if a non-integral value is present).

Nothing is imputed. Missing means missing. The counts are exposed under
`data_quality` in `GET /analytics/overview`.

## 2. Descriptive statistics (`descriptive.py`)

For the valid (non-missing) values of one column: count, missing, mean, median,
sample standard deviation (ddof = 1, missing for a single value), minimum,
maximum, quartiles (linear interpolation) and sum. In the API, `sum` is only
reported for additive count metrics.

## 3. Ranking (`ranking.py`)

Top-N by a metric, excluding rows without a valid value. Ties keep the
original row order (stable sort), so results are deterministic. For rank-type
metrics the API defaults to ascending order (rank 1 first).

## 4. Aggregation (`aggregation.py`)

- **By type**: one row per `Type`; missing types are grouped as `"Unknown"`.
- **By genre**: `Genres` is split on commas and each anime is counted **in full
  for every genre it lists**. A three-genre anime appears in three genre rows,
  so genre totals add up to more than the dataset total. This answers "how big
  is this genre?"; it does not partition the audience. Titles with no genre
  are left out.
- Each group reports `anime_count` (titles with a valid metric value), `total`,
  `mean` and `median`. Groups can be filtered with `min_anime` and sorted by any
  of those columns.

## 5. Distribution (`distribution.py`)

Percentiles (25, 50, 75, 90, 95, 99; linear interpolation), mean, median,
standard deviation, **bias-corrected sample skewness** and **bias-corrected
excess kurtosis** (0 for a normal distribution), plus an equal-width histogram
between the observed minimum and maximum (1–100 bins; bins are half-open except
the last). Skewness needs at least 3 values and kurtosis at least 4; otherwise
they are `null`.

Most count metrics here are extremely right-skewed (e.g. `Plan to Watch`
skewness is about 5.7), so equal-width histograms put nearly all titles in the
first bin. Read the percentiles first.

## 6. Engagement (`engagement.py`)

Definitions are in [`data_dictionary.md`](data_dictionary.md). Rates are
averaged **per title** (each anime counts once whatever its audience size),
grouped by type. Rates for tiny audiences are noisy; use `min_members` to
exclude them. These are user-list statistics from MyAnimeList, not measures of
viewing or streaming.

## 7. Pareto / decile analysis (`pareto.py`)

`calculate_pareto(data, metric_column, n)` follows this procedure:

1. Convert the metric to numbers; drop missing, non-numeric and infinite values.
2. Sort by the metric in descending order.
3. Rank with `rank(method="first", ascending=False)`, so tied values get
   distinct ranks (ties are broken by row order).
4. Cut the ranks into `n` approximately equal-sized groups with `pd.qcut`.
5. Divide each group's sum by the overall total.
6. Sort the proportions in descending order and label them `Group 1` …
   `Group n`.
7. Return a float `Series`; the values sum to 1 (within floating-point error).

What the result means:

- Groups are equal in **number of anime**, not in share of the metric. The
  output shows how concentrated the metric is. It does not assume or
  guarantee an 80/20 split.
- Because the labels are assigned after sorting proportions, `Group 1` is
  always the largest share. When `n` does not divide the number of
  observations evenly, group sizes differ by at most one, and with tied values
  a lower-ranked group could in principle be larger than a higher-ranked one.
- `cumulative_proportion` in the API is the running sum in that sorted order.

Error handling (all raise `AnalysisError`, a `ValueError`; the API returns 400
for data-dependent failures and 422 for invalid parameters):

| Case | Behaviour |
|---|---|
| `n` not a positive integer (0, negative, float, string, bool) | error |
| Unknown column | error |
| Empty dataset | error |
| No valid numeric values | error |
| Negative values | error (not meaningful for shares) |
| Fewer valid observations than `n` | error |
| Total of zero | error (no division by zero) |
| Missing / non-numeric values | excluded, not treated as zero |
| Duplicate metric values | handled by `rank(method="first")` |

### Deliberate deviations from the brief

- The function takes the DataFrame as its first argument (the original README
  sketch showed only `metric_column` and `n`), so it can be tested without the
  application.
- The API only accepts additive **count** metrics for Pareto analysis. `Score`
  (an average) and `Ranked`/`Popularity` (positions) are rejected with 422
  because shares of them have no meaning. The underlying function itself works
  on any non-negative numeric column.
- `pd.qcut(..., duplicates="drop")` from the earlier skeleton was removed.
  With `rank(method="first")` bin edges are always distinct, and dropping bins
  would silently return fewer than `n` groups.

### Reading real results

On the dataset used during development (17,562 titles), the top decile held:

| Metric | Top 10% share | Top 20% share |
|---|---|---|
| Members | 80.8% | 92.6% |
| Completed | 84.2% | 94.6% |
| Favorites | 96.1% | 98.9% |

Engagement is more concentrated than 80/20 in this dataset, which is a result
of the data, not of the method.
