# Anime Analytics API

A REST API that analyses the MyAnimeList anime dataset, built with Python,
Pandas, NumPy and FastAPI. It exposes anime lookup, filtering and pagination,
summary statistics, rankings, genre and type comparisons, engagement rates,
metric distributions and Pareto (decile) concentration analysis.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458)
![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC)

## Contents

1. [Problem statement](#1-problem-statement)
2. [Objectives](#2-objectives)
3. [Dataset](#3-dataset)
4. [Technology stack](#4-technology-stack)
5. [Architecture](#5-architecture)
6. [Repository structure](#6-repository-structure)
7. [Installation](#7-installation)
8. [Configuration](#8-configuration)
9. [Running the API](#9-running-the-api)
10. [API reference](#10-api-reference)
11. [Pareto analysis](#11-pareto-analysis)
12. [Error handling](#12-error-handling)
13. [Testing and code quality](#13-testing-and-code-quality)
14. [Data limitations](#14-data-limitations)
15. [Future extensions](#15-future-extensions)
16. [License and attribution](#16-license-and-attribution)

## 1. Problem statement

Anime platforms hold thousands of titles with very different audience sizes.
Understanding how ratings, popularity and engagement are distributed helps
analysts study content popularity and discovery.

**How can raw anime metadata be turned into a reliable, tested REST API that
delivers analytical insight into popularity, ratings, audience engagement and
how concentrated those metrics are?**

## 2. Objectives

- Load, validate and clean the dataset reproducibly, with documented rules.
- Implement the analysis in pure, independently testable Python functions.
- Expose it through a validated, documented FastAPI application.
- Provide filtering, sorting, pagination and identifier lookup.
- Implement a generalised Pareto/decile analysis.
- Cover everything with automated tests and keep the code typed and linted.

## 3. Dataset

**MyAnimeList Database 2020**, file `anime.csv`: 17,562 anime, 35 columns.

- Original repository: <https://github.com/Hernan4444/MyAnimelist-Database>
- Kaggle: <https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020>

`anime.csv` is **not included** in this repository or the delivered ZIP;
download it first, as described in [`data/README.md`](data/README.md), and place
it at `data/anime.csv` (or point `DATA_PATH` at it). Check the source's terms
before redistributing it.

Columns, types and the meaning of each metric are in
[`docs/data_dictionary.md`](docs/data_dictionary.md). The cleaning rules and
statistical definitions are in
[`docs/analytical_methodology.md`](docs/analytical_methodology.md). In short:
`Unknown` and empty text become missing values, impossible values (negative
counts, a score outside 0–10, rank 0) become missing, duplicate `MAL_ID`s keep
their first row, and **nothing is imputed**. A summary of what was changed is
returned by `GET /analytics/overview` under `data_quality`.

## 4. Technology stack

| Technology | Use |
|---|---|
| Python 3.11+ | Language |
| FastAPI, Uvicorn | API framework and ASGI server |
| Pydantic, pydantic-settings | Validation, response schemas, configuration |
| Pandas, NumPy | Data handling and analysis |
| Pytest, HTTPX | Tests (HTTPX backs FastAPI's `TestClient`) |
| Ruff | Linting and formatting |
| Mypy | Static typing of `src/` |
| uv (optional) | Dependency locking (`uv.lock`) |

## 5. Architecture

```text
Client -> FastAPI routes -> Services -> Repository -> Preprocessing -> anime.csv
                                   \-> Analytics functions (pure pandas/numpy)
```

The CSV is read **once at startup**, cleaned and kept in memory; requests never
touch the file. Analytics functions take a DataFrame and know nothing about
HTTP. Details: [`docs/architecture.md`](docs/architecture.md).

## 6. Repository structure

```text
anime-analytics-api/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── data/
│   ├── README.md                 how to obtain anime.csv
│   └── html/                     sample scraped pages (unused by the API)
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── analytical_methodology.md
├── src/anime_analytics/
│   ├── main.py                   app factory, startup, error handlers
│   ├── config.py                 settings (env / .env)
│   ├── exceptions.py
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/{anime,analytics}.py
│   ├── schemas/{anime,analytics,common}.py
│   ├── services/{anime_service,analytics_service}.py
│   ├── repositories/anime_repository.py
│   └── analytics/
│       ├── metrics.py            supported-metric registry, shared helpers
│       ├── preprocessing.py
│       ├── descriptive.py
│       ├── ranking.py
│       ├── aggregation.py        genre / type / category
│       ├── distribution.py
│       ├── engagement.py
│       └── pareto.py
└── tests/
```

## 7. Installation

Requires Python 3.11 or newer. The commands below were run on Linux with Python
3.13; the PowerShell variants differ only in how the environment is activated.

**Windows PowerShell**

```powershell
cd anime-analytics-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If activation is blocked, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.

**macOS / Linux**

```bash
cd anime-analytics-api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**With uv** (uses the committed `uv.lock`)

```bash
uv sync --extra dev
```

Then download the dataset (see [`data/README.md`](data/README.md)):

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Hernan4444/MyAnimelist-Database/master/data/anime.csv" -OutFile "data/anime.csv"
```

## 8. Configuration

Settings come from environment variables or a `.env` file in the working
directory. Copy the template and edit it if needed:

```bash
cp .env.example .env          # PowerShell: Copy-Item .env.example .env
```

| Variable | Default | Meaning |
|---|---|---|
| `APP_NAME` | `Anime Analytics API` | Title shown in the API and docs |
| `APP_ENV` | `development` | Free-text environment label (shown at `/`) |
| `DATA_PATH` | `data/anime.csv` | Path to `anime.csv`; relative paths resolve from the working directory |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL` |

No secrets are used. `.env` is git-ignored.

## 9. Running the API

From the project root, with the virtual environment active:

```bash
uvicorn anime_analytics.main:app --app-dir src --reload
```

(With `pip install -e .` the `--app-dir src` option is optional.)
Open <http://127.0.0.1:8000/docs> for the interactive documentation, or
<http://127.0.0.1:8000/openapi.json> for the schema.

Check that the dataset loaded:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","dataset_loaded":true,"anime_count":17562}
```

If `data/anime.csv` is missing the server still starts; `/health` returns
`"status": "degraded"` and data endpoints return `503`.

## 10. API reference

Interactive documentation with every parameter is at `/docs`. Summary:

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health check and dataset status |
| GET | `/anime` | List anime: filter, sort, paginate |
| GET | `/anime/{mal_id}` | One anime by MyAnimeList id |
| GET | `/analytics/overview` | Summary statistics and data-quality counts |
| GET | `/analytics/top-anime` | Rank anime by a metric |
| GET | `/analytics/genres` | Aggregate a metric by genre |
| GET | `/analytics/types` | Compare anime types (TV, Movie, ...) |
| GET | `/analytics/engagement` | Completion, drop and favorite rates by type |
| GET | `/analytics/distribution/{metric}` | Percentiles, skewness, histogram |
| GET | `/analytics/pareto` | Ranked-group concentration (Pareto/decile) |

Supported metrics: `Score`, `Episodes`, `Ranked`, `Popularity`, `Members`,
`Favorites`, `Watching`, `Completed`, `On-Hold`, `Dropped`, `Plan to Watch`
and `Score-1` … `Score-10`. Any other name is rejected with 422. `Pareto`
accepts only the additive count metrics (not `Score`, `Ranked` or `Popularity`).

### `GET /anime`

| Parameter | Default | Notes |
|---|---|---|
| `anime_type` | – | Exact type, case-insensitive (`TV`, `Movie`, `OVA`, ...) |
| `genre` | – | Exact genre name, case-insensitive (`action` matches `Action`; `act` does not) |
| `name` | – | Case-insensitive substring of the title or English title |
| `min_score`, `max_score` | – | 0–10, inclusive; unscored anime never match |
| `sort_by` | `MAL_ID` | `MAL_ID`, `Name`, `Score`, `Episodes`, `Ranked`, `Popularity`, `Members`, `Favorites`, `Watching`, `Completed`, `On-Hold`, `Dropped`, `Plan to Watch` |
| `order` | `asc` | `asc` or `desc`; missing values always sort last |
| `limit` | 20 | 1–100 |
| `offset` | 0 | ≥ 0 |

Filters combine with AND. Records use the dataset's column names; `Genres` is
a list and missing values are `null`.

```http
GET /anime?genre=Action&anime_type=TV&min_score=8&sort_by=Score&order=desc&limit=2
```

```json
{
  "total": 114,
  "limit": 2,
  "offset": 0,
  "count": 2,
  "items": [
    {
      "MAL_ID": 5114,
      "Name": "Fullmetal Alchemist: Brotherhood",
      "Score": 9.19,
      "Genres": ["Action", "Military", "Adventure", "Comedy", "Drama", "Magic", "Fantasy", "Shounen"],
      "Type": "TV",
      "Episodes": 64,
      "...": "remaining fields omitted here"
    }
  ]
}
```

(The example is abridged; `total` and the first item are from the dataset
checked while building this project and may differ with another copy.)

### `GET /analytics/top-anime`

`metric` (default `Members`), `limit` (1–100, default 10), `order` (`asc` or
`desc`; defaults to `desc`, or `asc` for `Ranked`/`Popularity` where lower is
better). Anime with no value for the metric are excluded.

```http
GET /analytics/top-anime?metric=Members&limit=3
```

```json
{
  "metric": "Members", "order": "desc", "limit": 3, "count": 3,
  "items": [
    {"rank": 1, "mal_id": 1535, "name": "Death Note", "type": "TV", "value": 2589552.0},
    {"rank": 2, "mal_id": 16498, "name": "Shingeki no Kyojin", "type": "TV", "value": 2531397.0},
    {"rank": 3, "mal_id": 5114, "name": "Fullmetal Alchemist: Brotherhood", "type": "TV", "value": 2248456.0}
  ]
}
```

### `GET /analytics/genres` and `/analytics/types`

`metric`, `sort_by` (`total`, `mean`, `median`, `anime_count`; default `total`
for count metrics and `mean` for `Score`/rank metrics), `order`, `min_anime`.
`/analytics/genres` also takes `limit` (1–200, default 50). An anime is
counted in full for every genre it lists, so genre totals exceed the dataset
total. `total` is `null` for non-additive metrics.

### `GET /analytics/distribution/{metric}`

`bins` (1–100, default 10). Returns count, missing, min, max, mean, median,
standard deviation, percentiles (`p25` … `p99`), skewness, excess kurtosis and
an equal-width histogram.

### `GET /analytics/engagement`

`min_members` (default 0) excludes small audiences. Returns, per type, the
number of titles, total members and the mean completion, drop and favorite
rates (definitions in the data dictionary).

## 11. Pareto analysis

```http
GET /analytics/pareto?metric=Completed&n=5
```

```json
{
  "metric": "Completed",
  "groups": 5,
  "observations": 17562,
  "excluded_missing": 0,
  "total": 388042424.0,
  "results": [
    {"group": "Group 1", "proportion": 0.94586, "cumulative_proportion": 0.94586},
    {"group": "Group 2", "proportion": 0.04400, "cumulative_proportion": 0.98986},
    {"group": "Group 3", "proportion": 0.00823, "cumulative_proportion": 0.99809},
    {"group": "Group 4", "proportion": 0.00157, "cumulative_proportion": 0.99965},
    {"group": "Group 5", "proportion": 0.00035, "cumulative_proportion": 1.00000}
  ]
}
```

(Values shown rounded; these are real results for the dataset checked.)

The anime are ranked by the metric (`rank(method="first")`, so ties get
distinct ranks), split into `n` almost equal-sized groups with `pd.qcut`, and
each group's sum is divided by the overall total. Groups are equal in *number
of anime*, not in share of the metric, and nothing assumes an 80/20 outcome:
in this dataset the top 10% of titles hold about 84% of all completions.

As a library function:

```python
from anime_analytics.analytics.pareto import calculate_pareto

shares = calculate_pareto(df, "Completed", n=10)  # pandas Series, sums to 1.0
```

Edge cases (invalid `n`, unknown metric, too few observations, missing,
negative or all-zero values, empty data) and the exact algorithm are
documented in [`docs/analytical_methodology.md`](docs/analytical_methodology.md).

## 12. Error handling

| Status | When |
|---|---|
| 200 | Success. Pages past the end of the data return an empty `items` list. |
| 400 | Parameters are valid but the analysis cannot run (for example more Pareto groups than observations). |
| 404 | Unknown `mal_id`. |
| 422 | Invalid parameter: wrong type, out of range, unsupported metric or sort field, `min_score > max_score`. |
| 503 | The dataset is not loaded. |

Every error body is `{"detail": ...}`. Responses never contain stack traces or
local file paths (those are logged server-side only), and never contain `NaN`
or `Infinity`: missing numbers are `null`.

## 13. Testing and code quality

Run from the project root with the virtual environment active.

```bash
pytest                      # all tests
pytest -m "not integration" # only the fast synthetic-data tests
ruff check .                # lint
ruff format --check .       # formatting
mypy src/                   # static types
```

The unit tests use a small synthetic table whose expected values are worked
out by hand (`tests/conftest.py`). Tests marked `integration` run against the
real `anime.csv` and are **skipped automatically** if it is not found at
`DATA_PATH` / `data/anime.csv`.

Results when this version was finished (Python 3.13, pandas 3.0, FastAPI 0.143):

| Command | Result |
|---|---|
| `pytest` with `data/anime.csv` present | 253 passed |
| `pytest` without the dataset | 219 passed, 34 skipped |
| `ruff check .` | All checks passed |
| `ruff format --check .` | No files to reformat |
| `mypy src/` | No issues in 27 source files |

Only `src/` is type-checked; the tests are not annotated. Python 3.11 and 3.12
were not available in the environment used, so they have not been tested
(the code targets `>=3.11`).

## 14. Data limitations

- The data is a **2020/early-2021 snapshot** of MyAnimeList, not live data.
- `Members`, `Completed`, etc. count **MyAnimeList list entries**, not viewers
  or streams, and reflect MyAnimeList's user base only.
- About 29% of titles have no `Score`; they are excluded from score
  statistics rather than treated as zero.
- `Popularity` and `Ranked` are ranks (lower is better), not quantities, and are
  not comparable with counts.
- Genre totals double-count multi-genre titles by design.
- Correlation in these aggregates is not evidence of causation.

## 15. Future extensions

Not implemented; possible next steps:

- Docker image and GitHub Actions CI.
- Persistence in PostgreSQL via SQLAlchemy.
- Studio-level benchmarking and genre co-occurrence analysis.
- Content-based recommendation using synopsis similarity.
- Response caching and performance benchmarking.

## 16. License and attribution

Code: MIT License, see [`LICENSE`](LICENSE).

Data: the MyAnimeList Database 2020 dataset by Hernan4444, compiled from
MyAnimeList (<https://myanimelist.net/>). It is third-party data and is not
covered by this project's license; review the source's terms before
redistributing it.
