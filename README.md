# Anime Analytics API

A tested, documented REST API for exploring the MyAnimeList anime dataset using Python, Pandas, NumPy and FastAPI. The application provides anime lookup, filtering, pagination, statistical summaries, rankings, genre and type comparisons, engagement metrics, metric distributions, and Pareto (decile) concentration analysis.

[![CI](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml/badge.svg)](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458)
![Testing](https://img.shields.io/badge/Testing-Pytest-0A9EDC)
![Documentation](https://img.shields.io/badge/Documentation-MkDocs%20Material-526CFE)
![License](https://img.shields.io/badge/License-MIT-green)

## Contents

1. [Overview](#1-overview)
2. [Objectives](#2-objectives)
3. [Dataset](#3-dataset)
4. [Technology stack](#4-technology-stack)
5. [Architecture](#5-architecture)
6. [Repository structure](#6-repository-structure)
7. [Installation](#7-installation)
8. [Configuration](#8-configuration)
9. [Running the API](#9-running-the-api)
10. [API reference](#10-api-reference)
11. [Analytical methodology](#11-analytical-methodology)
12. [Testing and code quality](#12-testing-and-code-quality)
13. [Documentation with MkDocs](#13-documentation-with-mkdocs)
14. [Building and validating documentation](#14-building-and-validating-documentation)
15. [Publishing documentation](#15-publishing-documentation)
16. [Data limitations](#16-data-limitations)
17. [Future extensions](#17-future-extensions)
18. [License and attribution](#18-license-and-attribution)

## 1. Overview

Anime platforms contain thousands of titles with varying ratings, audience sizes, and engagement metrics. This project turns anime metadata into a structured REST API for querying the dataset and exploring statistical patterns.

The application separates HTTP handling, business logic, data access, preprocessing, and analytical functions. It includes automated tests, configuration management, technical documentation, and a GitHub Actions continuous integration workflow.

### Key features

- Search, filter, sort, and paginate anime records.
- Retrieve individual anime using MyAnimeList IDs.
- Calculate dataset summaries and data-quality statistics.
- Rank anime using supported numerical metrics.
- Compare genres and anime types.
- Analyze completion, drop, and favorite rates.
- Examine metric distributions, percentiles, skewness, and kurtosis.
- Analyze metric concentration through Pareto/decile grouping.
- Validate requests and return structured error responses.
- Run automated tests and code-quality checks.
- Browse detailed technical documentation using MkDocs Material.

## 2. Objectives

- Load, validate, and clean the dataset reproducibly.
- Implement independently testable analytical functions.
- Expose analytics through a validated FastAPI application.
- Provide filtering, sorting, pagination, and identifier lookup.
- Implement generalized Pareto/decile analysis.
- Maintain automated testing and code-quality checks.
- Document the architecture, API behavior, analytical assumptions, and development workflow.

## 3. Dataset

The application uses the **MyAnimeList Database 2020** dataset, specifically `anime.csv`, which contains 17,562 anime and 35 columns in the version used during development.

Sources:

- Original repository: https://github.com/Hernan4444/MyAnimelist-Database
- Kaggle dataset: https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020
- MyAnimeList: https://myanimelist.net/

The dataset is not included in this repository. Obtain it separately and place it at `data/anime.csv`, or configure `DATA_PATH` to point to the file.

See [`data/readme.md`](data/readme.md) for dataset instructions.

### Data preprocessing

The preprocessing pipeline applies documented rules:

- `Unknown` and empty text values become missing values.
- Impossible values, such as negative counts, scores outside 0–10, and rank 0, become missing.
- Duplicate `MAL_ID` values retain their first row.
- Missing values are not imputed.

Data-quality information is available through `GET /analytics/overview`.

Detailed documentation:

- [Data dictionary](docs/data_dictionary.md)
- [Analytical methodology](docs/analytical_methodology.md)

Review the dataset source's terms before redistributing the data.

## 4. Technology stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic and pydantic-settings | Validation and configuration |
| Pandas and NumPy | Data processing and analysis |
| Pytest and HTTPX | Automated testing |
| Ruff | Linting and formatting |
| Mypy | Static type checking |
| uv | Optional dependency and lockfile management |
| GitHub Actions | Continuous integration |
| MkDocs Material | Technical documentation website |

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

Services
  |
  v
Analytics functions (Pandas / NumPy)
```

The CSV is loaded and processed at application startup, then kept in memory. Requests do not repeatedly read the file.

Analytical functions operate on DataFrames independently of HTTP handling. This separation supports testing, maintainability, and reuse.

See [`docs/architecture.md`](docs/architecture.md) for the detailed architecture.

## 6. Repository structure

```text
Anime-Analytics-API/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── .gitattributes
├── pyproject.toml
├── uv.lock
├── mkdocs.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── readme.md
│   └── html/
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── architecture.md
│   ├── analytical_methodology.md
│   ├── data_dictionary.md
│   └── development.md
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

The `data/html/` directory contains supplementary files and is not required by the API. The dataset CSV is excluded from version control.

The MkDocs source files are maintained in `docs/`, while `mkdocs.yml` defines the documentation website's configuration and navigation. The generated website is written to `site/` and should not be committed.

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

If PowerShell blocks activation, run:

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

If uv is installed and the lockfile is up to date:

```bash
uv sync --extra dev
```

### Download the dataset

From the project root:

```powershell
New-Item -ItemType Directory -Force data | Out-Null

Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/Hernan4444/MyAnimelist-Database/master/data/anime.csv" `
  -OutFile "data/anime.csv"
```

Alternatively, download the dataset from its source and place it at `data/anime.csv`.

## 8. Configuration

The application reads configuration from environment variables or a local `.env` file.

Create the file from the template:

```powershell
Copy-Item .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Anime Analytics API` | Application title |
| `APP_ENV` | `development` | Environment label |
| `DATA_PATH` | `data/anime.csv` | Dataset location |
| `LOG_LEVEL` | `INFO` | Logging level |

Supported logging levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.

The local `.env` file should remain excluded from version control. Do not commit credentials or other secrets.

## 9. Running the API

From the project root, with the virtual environment activated:

```powershell
uvicorn anime_analytics.main:app --app-dir src --reload
```

The API is available locally at:

- Interactive documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Health endpoint: http://127.0.0.1:8000/health

The `--reload` option is intended for development.

### Health check

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

When the dataset is loaded, the health endpoint should report a healthy status and the number of available anime records.

If the dataset is missing, the application can start in a degraded state. Data-dependent endpoints return `503`.

## 10. API reference

The interactive API documentation at `/docs` exposes the request parameters and schemas generated by FastAPI.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health and dataset status |
| GET | `/anime` | Filtering, sorting, and pagination |
| GET | `/anime/{mal_id}` | Retrieve anime by ID |
| GET | `/analytics/overview` | Summary statistics and data quality |
| GET | `/analytics/top-anime` | Rank anime by a metric |
| GET | `/analytics/genres` | Aggregate metrics by genre |
| GET | `/analytics/types` | Compare anime types |
| GET | `/analytics/engagement` | Engagement analysis |
| GET | `/analytics/distribution/{metric}` | Metric distributions |
| GET | `/analytics/pareto` | Pareto/decile concentration analysis |

### Supported metrics

The API supports:

`Score`, `Episodes`, `Ranked`, `Popularity`, `Members`, `Favorites`, `Watching`, `Completed`, `On-Hold`, `Dropped`, `Plan to Watch`, and `Score-1` through `Score-10`.

Unsupported metric names return `422`.

Pareto analysis accepts additive count metrics rather than `Score`, `Ranked`, or `Popularity`.

### Anime filtering

The `GET /anime` endpoint supports:

| Parameter | Default | Description |
|---|---|---|
| `anime_type` | None | Exact anime type, case-insensitive |
| `genre` | None | Exact genre name, case-insensitive |
| `name` | None | Case-insensitive substring search |
| `min_score` | None | Minimum score, inclusive |
| `max_score` | None | Maximum score, inclusive |
| `sort_by` | `MAL_ID` | Supported sorting field |
| `order` | `asc` | `asc` or `desc` |
| `limit` | `20` | Page size, 1–100 |
| `offset` | `0` | Non-negative number of records to skip |

Filters combine using AND. Missing values sort last, and unscored anime do not match score filters.

Example:

```http
GET /anime?genre=Action&anime_type=TV&min_score=8&sort_by=Score&order=desc&limit=5
```

### Anime ranking

Example:

```http
GET /analytics/top-anime?metric=Members&limit=10
```

The default metric is `Members`. Missing values for the selected metric are excluded. `Ranked` and `Popularity` use ascending order by default because lower rank values indicate better rankings.

### Genre and type analysis

The genre and type endpoints aggregate selected metrics using supported aggregation modes, including `total`, `mean`, `median`, and `anime_count`.

Genre totals can exceed the total number of anime because a title can belong to multiple genres.

### Metric distributions

Example:

```http
GET /analytics/distribution/Score?bins=10
```

The response includes descriptive statistics, percentiles, skewness, excess kurtosis, and an equal-width histogram.

### Engagement analysis

Example:

```http
GET /analytics/engagement?min_members=100
```

The endpoint reports title counts, total members, and mean completion, drop, and favorite rates by anime type.

### Error handling

| Status code | Meaning |
|---|---|
| `200` | Request succeeded |
| `400` | Analysis cannot be performed with the supplied valid parameters |
| `404` | Anime ID not found |
| `422` | Invalid parameter or unsupported value |
| `503` | Dataset unavailable |

See [`docs/api-reference.md`](docs/api-reference.md) for the expanded endpoint guide.

## 11. Analytical methodology

The project includes descriptive statistics, rankings, genre and type aggregation, engagement rates, distributions, and Pareto/decile concentration analysis.

### Pareto analysis

Example:

```http
GET /analytics/pareto?metric=Completed&n=10
```

Anime are ranked using `rank(method="first")` and divided into approximately equal-sized groups using `pd.qcut`. Each group's metric sum is divided by the overall total.

Groups are equal in the **number of anime**, not in their share of the metric. The method does not assume that an 80/20 distribution must occur.

For the dataset examined during development, the top 10% of titles accounted for approximately 84% of recorded completions. This is a dataset-specific observation, not a universal property of anime popularity.

The implementation handles invalid group counts, unsupported metrics, insufficient observations, missing values, negative values, all-zero data, and empty input according to the documented methodology.

Detailed references:

- [`docs/analytical_methodology.md`](docs/analytical_methodology.md)
- [`docs/data_dictionary.md`](docs/data_dictionary.md)

## 12. Testing and code quality

Run the checks from the project root with the virtual environment activated.

### Automated tests

```powershell
python -m pytest -v
```

To run tests that do not require the real dataset:

```powershell
python -m pytest -m "not integration"
```

Integration tests use `anime.csv` and are skipped automatically when the dataset is unavailable, according to the project's test configuration.

### Code quality

```powershell
ruff check .
ruff format --check .
mypy src/
```

### Continuous integration

GitHub Actions runs the configured CI workflow on pushes to `main` and pull requests targeting `main`.

The workflow installs the project and development dependencies, runs the test suite, and executes Ruff lint checks.

- [GitHub Actions workflow](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions)
- [CI configuration](.github/workflows/ci.yml)

The CI badge at the top of this README reflects the workflow status.

Previously reported development results included 253 passing tests with the dataset present, 219 passing and 34 skipped without it, successful Ruff checks, and no Mypy issues in 27 source files. These are historical results, not a guarantee that every future commit will produce identical results.

## 13. Documentation with MkDocs

The project uses **MkDocs Material** to organize its technical documentation into a searchable website with navigation, syntax-highlighted code blocks, and responsive presentation.

### Documentation structure

| File | Purpose |
|---|---|
| `mkdocs.yml` | Site configuration, theme, and navigation |
| `docs/index.md` | Documentation homepage |
| `docs/getting-started.md` | Installation and local setup |
| `docs/api-reference.md` | Endpoint guide and request examples |
| `docs/architecture.md` | Application architecture |
| `docs/analytical_methodology.md` | Statistical methods and assumptions |
| `docs/data_dictionary.md` | Dataset fields and metric definitions |
| `docs/development.md` | Testing, code quality, and development workflow |

The main `README.md` remains the repository's landing page. The MkDocs site provides a more structured guide for developers who need detailed instructions.

### Install documentation dependencies

Activate the project virtual environment and install MkDocs Material:

```powershell
python -m pip install mkdocs-material
```

If MkDocs Material has already been added to the project's development dependencies, install all development dependencies using:

```powershell
python -m pip install -e ".[dev]"
```

Verify the installation:

```powershell
mkdocs --version
```

### Preview locally

From the repository root:

```powershell
mkdocs serve --dev-addr 127.0.0.1:8001
```

Open http://127.0.0.1:8001 in your browser.

MkDocs watches the Markdown source files and rebuilds the preview when they change.

### Documentation configuration

The root-level `mkdocs.yml` defines the site name, repository links, Material theme, Markdown extensions, and navigation.

The `docs/` directory contains the source Markdown files. The generated website is written to `site/`.

The generated `site/` directory should be excluded from version control.

## 14. Building and validating documentation

Before publishing, validate the documentation independently of the API.

### Strict build

```powershell
mkdocs build --strict
```

This generates the static website and treats MkDocs warnings as errors.

Resolve missing navigation pages, invalid configuration, and other build warnings before publishing.

### Inspect generated output

```powershell
Get-ChildItem .\site\
```

The output should include `index.html`, HTML pages for the navigation entries, and supporting static assets.

### Final validation checklist

- The local documentation website loads.
- Every navigation item opens the correct page.
- Existing architecture, methodology, and data dictionary content is preserved.
- Code blocks, tables, and internal links render correctly.
- Search works as expected.
- `mkdocs build --strict` completes without warnings.
- Backend tests and configured quality checks pass.
- Generated `site/` files are not accidentally committed.

## 15. Publishing documentation

The documentation source can be committed to the main repository independently of publishing the website.

### Commit documentation source

```powershell
git status
git add mkdocs.yml docs/ pyproject.toml .gitignore
git diff --cached --check
git diff --cached --stat
```

Review the staged changes, then commit and push:

```powershell
git commit -m "Add MkDocs project documentation"
git push origin main
```

Include only files that you have actually created or modified. Do not stage unrelated changes unintentionally.

### Publish using GitHub Pages

After the local documentation build passes, the site can be published to GitHub Pages.

A manual deployment can be initiated with:

```powershell
mkdocs gh-deploy
```

This command builds the documentation and publishes it to the `gh-pages` branch, subject to the repository's permissions and deployment configuration.

Ensure that GitHub Pages is configured to serve from the appropriate branch. Review the resulting deployment status in GitHub Actions.

The intended documentation URL is:

https://sunilnarayan419-ui.github.io/Anime-Analytics-API/

**This URL is not evidence that the website is already published.** It becomes usable after the deployment succeeds and GitHub Pages is configured correctly.

For automated publication, a separate GitHub Actions documentation workflow can build the site and deploy it when documentation changes are pushed. Keep the existing API CI workflow intact.

## 16. Data limitations

- The dataset is a 2020/early-2021 snapshot, not live data.
- `Members`, `Completed`, and related fields count MyAnimeList list entries, not verified unique viewers or streams.
- Metrics reflect the MyAnimeList user base only.
- Approximately 29% of titles in the examined dataset have no score; these are excluded from score statistics rather than treated as zero.
- `Popularity` and `Ranked` are ranks, not quantities, and are not directly comparable to counts.
- Genre totals double-count multi-genre titles by design.
- Correlation in aggregated data is not evidence of causation.
- Results depend on the dataset version supplied to the application.

## 17. Future extensions

The current version provides a tested, documented FastAPI backend and a structured MkDocs documentation source.

Potential future improvements include:

- **Containerization:** Package the API using Docker for reproducible deployment.
- **Persistent storage:** Introduce PostgreSQL and SQLAlchemy if database-backed storage becomes necessary.
- **Advanced analytics:** Explore studio-level benchmarking and genre co-occurrence analysis.
- **Recommendation systems:** Investigate content-based recommendations using anime synopsis similarity.
- **Performance optimization:** Benchmark endpoint latency and throughput, then introduce caching where measurements justify it.
- **Automated documentation deployment:** Publish the MkDocs site through a dedicated GitHub Actions workflow.

These are future directions, not claims about functionality already implemented.

## 18. License and attribution

### Code

The project's code is released under the MIT License. See [`LICENSE`](LICENSE).

### Dataset

The project uses the MyAnimeList Database 2020 dataset by Hernan4444, compiled from MyAnimeList.

- Original repository: https://github.com/Hernan4444/MyAnimelist-Database
- MyAnimeList: https://myanimelist.net/
- Kaggle dataset: https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020

The dataset is third-party material and is not covered by this project's MIT License. Review the original source's terms before redistributing it.
