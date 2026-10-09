# Anime Analytics API

A REST API that analyses the MyAnimeList anime dataset, built with Python, Pandas, NumPy and FastAPI. It exposes anime lookup, filtering and pagination, summary statistics, rankings, genre and type comparisons, engagement rates, metric distributions and Pareto (decile) concentration analysis.

[![CI](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml/badge.svg)](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458)
![Testing](https://img.shields.io/badge/Testing-Pytest-0A9EDC)
![License](https://img.shields.io/badge/License-MIT-green)

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

Anime platforms hold thousands of titles with very different audience sizes. Understanding how ratings, popularity and engagement are distributed helps analysts study content popularity and discovery.

**How can raw anime metadata be turned into a reliable, tested REST API that delivers analytical insight into popularity, ratings, audience engagement and how concentrated those metrics are?**

## 2. Objectives

- Load, validate and clean the dataset reproducibly, with documented rules.
- Implement the analysis in pure, independently testable Python functions.
- Expose it through a validated, documented FastAPI application.
- Provide filtering, sorting, pagination and identifier lookup.
- Implement a generalised Pareto/decile analysis.
- Cover the application with automated tests and maintain typed, linted code.

## 3. Dataset

**MyAnimeList Database 2020**, file `anime.csv`: 17,562 anime, 35 columns.

- Original repository: https://github.com/Hernan4444/MyAnimelist-Database
- Kaggle: https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020

`anime.csv` is **not included** in this repository. Download it as described in [`data/readme.md`](data/readme.md), and place it at `data/anime.csv` or configure `DATA_PATH` to point to the file.

Check the original source's terms before redistributing the dataset.

Column definitions, types and metric meanings are documented in [`docs/data_dictionary.md`](docs/data_dictionary.md). Cleaning rules and statistical definitions are documented in [`docs/analytical_methodology.md`](docs/analytical_methodology.md).

In summary:

- `Unknown` and empty text values become missing values.
- Impossible values, including negative counts, scores outside 0–10 and rank 0, become missing.
- Duplicate `MAL_ID` values retain their first row.
- Missing values are not imputed.

A summary of the cleaning results is returned by `GET /analytics/overview` under `data_quality`.

## 4. Technology stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Programming language |
| FastAPI, Uvicorn | API framework and ASGI server |
| Pydantic, pydantic-settings | Validation, response schemas and configuration |
| Pandas, NumPy | Data processing and statistical analysis |
| Pytest, HTTPX | Automated testing |
| Ruff | Linting and formatting |
| Mypy | Static type checking of `src/` |
| uv | Optional dependency and lockfile management |
| GitHub Actions | Automated CI testing and code-quality checks |

## 5. Architecture

```text
Client
  |
  v
FastAPI routes
  |
  v
Services
  |
  v
Repository
  |
  v
Preprocessing
  |
  v
anime.csv

Services --> Analytics functions (pure Pandas/NumPy)
```

The CSV is read once at startup, cleaned and kept in memory. Requests do not repeatedly read the file.

Analytics functions operate on a DataFrame and are independent of HTTP handling.

For further details, see [`docs/architecture.md`](docs/architecture.md).

## 6. Repository structure

```text
anime-analytics-api/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── .gitattributes
├── pyproject.toml
├── uv.lock
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── readme.md
│   └── html/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── analytical_methodology.md
├── src/
│   └── anime_analytics/
│       ├── main.py
│       ├── config.py
│       ├── exceptions.py
│       ├── api/
│       │   ├── dependencies.py
│       │   └── routes/
│       │       ├── anime.py
│       │       └── analytics.py
│       ├── schemas/
│       │   ├── anime.py
│       │   ├── analytics.py
│       │   └── common.py
│       ├── services/
│       │   ├── anime_service.py
│       │   └── analytics_service.py
│       ├── repositories/
│       │   └── anime_repository.py
│       └── analytics/
│           ├── metrics.py
│           ├── preprocessing.py
│           ├── descriptive.py
│           ├── ranking.py
│           ├── aggregation.py
│           ├── distribution.py
│           ├── engagement.py
│           └── pareto.py
└── tests/
```

The `data/html/` directory contains supplementary sample files and is not required by the API. The actual CSV dataset is excluded from version control.

## 7. Installation

Requires Python 3.11 or newer.

### Windows PowerShell

```powershell
git clone https://github.com/sunilnarayan419-ui/Anime-Analytics-API.git
cd Anime-Analytics-API

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If PowerShell blocks environment activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### macOS / Linux

```bash
git clone https://github.com/sunilnarayan419-ui/Anime-Analytics-API.git
cd Anime-Analytics-API

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Using uv

If uv is installed, use the committed lockfile:

```bash
uv sync --extra dev
```

### Download the dataset

From the project root, download the CSV:

```powershell
New-Item -ItemType Directory -Force data | Out-Null

Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/Hernan4444/MyAnimelist-Database/master/data/anime.csv" `
  -OutFile "data/anime.csv"
```

Alternatively, obtain the dataset from the original source or Kaggle and place it at `data/anime.csv`.

The dataset is intentionally excluded from this repository.

## 8. Configuration

Settings are read from environment variables or a `.env` file in the working directory.

Create a local configuration file from the example:

```powershell
Copy-Item .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Anime Analytics API` | Application title shown in the API and documentation |
| `APP_ENV` | `development` | Environment label |
| `DATA_PATH` | `data/anime.csv` | Path to the dataset; relative paths resolve from the working directory |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL` |

No API credentials are required for the documented functionality. The local `.env` file is excluded from version control.

Do not commit actual credentials or other secrets if configuration requirements change.

## 9. Running the API

From the project root, with the virtual environment activated:

```powershell
uvicorn anime_analytics.main:app --app-dir src --reload
```

The API will be available at:

- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **OpenAPI schema:** http://127.0.0.1:8000/openapi.json
- **Health check:** http://127.0.0.1:8000/health

The `--reload` option is intended for development.

### Verify the health endpoint

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

When the dataset is loaded successfully, the response should indicate a healthy application and the dataset count.

If `data/anime.csv` is missing, the server can still start. The health endpoint reports a degraded status, and data-dependent endpoints return `503`.

## 10. API reference

Interactive documentation for all endpoints and parameters is available at `/docs`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health check and dataset status |
| GET | `/anime` | List anime with filtering, sorting and pagination |
| GET | `/anime/{mal_id}` | Retrieve one anime by MyAnimeList ID |
| GET | `/analytics/overview` | Summary statistics and data-quality counts |
| GET | `/analytics/top-anime` | Rank anime by a selected metric |
| GET | `/analytics/genres` | Aggregate a metric by genre |
| GET | `/analytics/types` | Compare anime types |
| GET | `/analytics/engagement` | Completion, drop and favorite rates by type |
| GET | `/analytics/distribution/{metric}` | Statistical distribution of a metric |
| GET | `/analytics/pareto` | Ranked-group concentration analysis |

### Supported metrics

Supported metrics include:

`Score`, `Episodes`, `Ranked`, `Popularity`, `Members`, `Favorites`, `Watching`, `Completed`, `On-Hold`, `Dropped`, `Plan to Watch` and `Score-1` through `Score-10`.

Unsupported metric names return `422`.

Pareto analysis accepts additive count metrics, not `Score`, `Ranked` or `Popularity`.

### `GET /anime`

Supported parameters:

| Parameter | Default | Description |
|---|---|---|
| `anime_type` | None | Exact anime type, case-insensitive |
| `genre` | None | Exact genre name, case-insensitive |
| `name` | None | Case-insensitive substring search across titles |
| `min_score` | None | Minimum score, inclusive, between 0 and 10 |
| `max_score` | None | Maximum score, inclusive, between 0 and 10 |
| `sort_by` | `MAL_ID` | Supported field used for sorting |
| `order` | `asc` | Sort direction: `asc` or `desc` |
| `limit` | `20` | Number of records per page, from 1 to 100 |
| `offset` | `0` | Number of records to skip; must be non-negative |

Filters combine with AND. Missing values sort last. Unscored anime do not match score filters.

Example request:

```http
GET /anime?genre=Action&anime_type=TV&min_score=8&sort_by=Score&order=desc&limit=2
```

The response includes pagination metadata and an `items` array containing anime records.

The dataset's column names are retained in returned records. `Genres` is represented as a list, and missing values are returned as `null`.

### `GET /anime/{mal_id}`

Returns one anime record for a valid MyAnimeList ID.

If the ID is not found, the API returns `404`.

### `GET /analytics/overview`

Returns dataset-level summary statistics and data-quality information, including preprocessing results.

### `GET /analytics/top-anime`

Parameters:

- `metric`: metric used for ranking; defaults to `Members`.
- `limit`: number of results, from 1 to 100; defaults to `10`.
- `order`: `asc` or `desc`. Defaults to descending, except `Ranked` and `Popularity`, where ascending order is used because lower ranks are better.

Anime without a value for the selected metric are excluded.

Example:

```http
GET /analytics/top-anime?metric=Members&limit=3
```

### `GET /analytics/genres` and `GET /analytics/types`

These endpoints aggregate a selected metric by genre or anime type.

Supported parameters include:

- `metric`
- `sort_by`: `total`, `mean`, `median` or `anime_count`
- `order`
- `min_anime`
- `limit` for the genre endpoint

The default aggregation is `total` for count metrics and `mean` for `Score` and rank metrics.

An anime is counted in full for every genre it lists, so genre totals can exceed the number of anime in the dataset. The `total` field is `null` for non-additive metrics.

### `GET /analytics/distribution/{metric}`

The `bins` parameter controls the number of histogram bins, from 1 to 100, with a default of 10.

The response includes count, missing values, minimum, maximum, mean, median, standard deviation, percentiles, skewness, excess kurtosis and an equal-width histogram.

### `GET /analytics/engagement`

The `min_members` parameter excludes titles below a specified audience size.

The response reports per-type title counts, total members and mean completion, drop and favorite rates. See the data dictionary for the metric definitions and limitations.

## 11. Pareto analysis

The Pareto endpoint studies how an additive metric is concentrated across ranked groups.

Example:

```http
GET /analytics/pareto?metric=Completed&n=5
```

The response contains:

- The selected metric.
- Number of groups.
- Number of observations.
- Excluded missing observations.
- Overall metric total.
- Each group's proportion and cumulative proportion.

### Methodology

Anime are ranked using `rank(method="first")`, giving tied values distinct ranks. The ranked observations are divided into `n` approximately equal-sized groups using `pd.qcut`.

Each group's metric sum is divided by the overall total.

Groups are equal in **number of anime**, not in their share of the metric. The method does not assume that an 80/20 distribution must occur.

For the dataset examined during development, the top 10% of titles accounted for approximately 84% of recorded completions. This is a dataset-specific observation, not a universal property of anime popularity.

### Using the analytical function directly

```python
from anime_analytics.analytics.pareto import calculate_pareto

shares = calculate_pareto(df, "Completed", n=10)
```

The function returns a pandas Series of group shares.

Edge cases, input validation and the exact algorithm are documented in [`docs/analytical_methodology.md`](docs/analytical_methodology.md).

## 12. Error handling

| Status code | Meaning |
|---|---|
| `200` | Request succeeded. Pages past the end of the data return an empty `items` list. |
| `400` | Parameters are valid, but the analysis cannot run, such as requesting more Pareto groups than observations. |
| `404` | Unknown MyAnimeList ID. |
| `422` | Invalid parameter, unsupported metric or sort field, incorrect type, out-of-range value or invalid score bounds. |
| `503` | Dataset is not loaded. |

Error responses use a `detail` field. Responses are designed not to expose stack traces or local file paths. Missing numeric values are represented as `null`, not `NaN` or `Infinity`.

## 13. Testing and code quality

The project includes automated tests for analytical functions, API endpoints, configuration, repository behavior, preprocessing and integration with the real dataset.

Run these commands from the project root with the virtual environment activated:

```powershell
python -m pytest -v
ruff check .
ruff format --check .
mypy src/
```

To run tests that do not require the real dataset:

```powershell
python -m pytest -m "not integration"
```

Integration tests use the real `anime.csv` and are skipped automatically when the dataset is unavailable at `DATA_PATH` or `data/anime.csv`.

### Continuous integration

GitHub Actions runs the configured CI workflow on pushes to `main` and pull requests targeting `main`.

The workflow installs the project and development dependencies, runs the test suite and executes Ruff lint checks on GitHub's runner.

**CI status:** [View GitHub Actions runs](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions).

The badge at the top of this README reflects the status of the configured workflow.

### Test results

The original development run reported the following results with Python 3.13, pandas 3.0 and FastAPI 0.143:

| Check | Previously reported result |
|---|---|
| Pytest with `data/anime.csv` present | 253 passed |
| Pytest without the dataset | 219 passed, 34 skipped |
| `ruff check .` | All checks passed |
| `ruff format --check .` | No files to reformat |
| `mypy src/` | No issues in 27 source files |

These figures describe the development run and should not be interpreted as the results of every subsequent commit. The current CI workflow's result is available in the GitHub Actions tab.

Only `src/` is type-checked; tests are not annotated. Python 3.11 and 3.12 were not available in the original development environment, so those versions were not verified there.

## 14. Data limitations

- The dataset is a **2020/early-2021 snapshot**, not live data.
- `Members`, `Completed` and related fields count MyAnimeList list entries, not unique viewers or streams.
- The metrics reflect MyAnimeList's user base only.
- Approximately 29% of titles in the examined dataset have no `Score`; these titles are excluded from score statistics rather than treated as zero.
- `Popularity` and `Ranked` are ranks, with lower values indicating better ranks. They are not quantities and are not directly comparable to counts.
- Genre totals double-count multi-genre titles by design.
- Correlation in aggregated data is not evidence of causation.
- Results depend on the dataset version supplied to the application.

## 15. Future extensions

The current version provides a tested, documented FastAPI backend for anime data exploration and statistical analytics.

The following are potential future directions and are **not part of the current implementation**:

- **Containerization:** Package the application using Docker for reproducible deployment.
- **Persistent storage:** Introduce PostgreSQL and SQLAlchemy if database-backed storage becomes necessary.
- **Advanced analytics:** Explore studio-level benchmarking and genre co-occurrence analysis.
- **Recommendation systems:** Investigate content-based recommendations using anime synopsis similarity.
- **Performance optimization:** Benchmark endpoint latency and throughput, then introduce caching where measurements justify it.

These improvements can be evaluated independently according to their practical value and complexity.

## 16. License and attribution

### Code

This project's code is released under the MIT License. See [`LICENSE`](LICENSE).

### Dataset

The project uses the MyAnimeList Database 2020 dataset by Hernan4444, compiled from MyAnimeList.

- Original repository: https://github.com/Hernan4444/MyAnimelist-Database
- MyAnimeList: https://myanimelist.net/
- Kaggle dataset: https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020

The dataset is third-party material and is **not covered by this project's MIT License**. Review the original source's terms before redistributing it.
