# Anime Analytics API

**A production-oriented data analytics REST API built with Python, Pandas, and FastAPI.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458)
![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

---

## 1. Problem Statement

### Background

Anime platforms contain thousands of titles with varying audience sizes, ratings, popularity rankings, and completion statistics. Understanding how audience engagement is distributed across these titles can help analysts investigate content popularity, audience preferences, and opportunities for content discovery.

The MyAnimeList Database 2020 dataset provides anime metadata and user engagement statistics that can be used to explore these patterns.

### Core Problem

**How can we transform raw anime metadata into a reliable, testable REST API that delivers meaningful analytical insights about anime popularity, ratings, audience engagement, and metric concentration?**

This project addresses the problem by combining data preprocessing, statistical analysis, and backend engineering in a modular Python application.

The API will allow users to retrieve anime records, filter and rank titles, inspect aggregated statistics, and perform Pareto or decile analysis through HTTP requests.

---

## 2. Project Objectives

- Build a reproducible data preprocessing pipeline.
- Analyze anime metadata using Pandas and NumPy.
- Develop a REST API using FastAPI.
- Implement filtering, sorting, pagination, and identifier-based lookup.
- Calculate descriptive statistics and genre-level summaries.
- Implement generalized Pareto analysis using ranked quantile groups.
- Validate request parameters and return consistent error responses.
- Write automated unit and integration tests.
- Document API contracts and analytical assumptions.
- Maintain a modular, code-first repository without Jupyter notebooks.

---

## 3. Dataset

**Dataset:** MyAnimeList Database 2020

- [Original dataset repository](https://github.com/Hernan4444/MyAnimelist-Database)
- [Kaggle dataset page](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)

### Primary data source

The initial version will use `anime.csv`, which contains anime metadata and audience statistics.

| Column | Analytical use |
|---|---|
| `MAL_ID` | Unique anime identifier |
| `Name` | Anime title |
| `Score` | Reported rating |
| `Genres` | Genre-based analysis |
| `Type` | Format-based comparison |
| `Episodes` | Episode count analysis |
| `Studios` | Studio-level aggregation |
| `Popularity` | Popularity ranking |
| `Members` | Audience membership analysis |
| `Favorites` | Favorite-count analysis |
| `Watching` | Current watching activity |
| `Completed` | Completion-count analysis |
| `Dropped` | Dropped-title activity |
| `On-Hold` | On-hold activity |
| `Plan to Watch` | Planned viewing activity |

Other files in the dataset may be introduced later if additional user-level or recommendation analyses become necessary.

**Data handling rule:** Keep the raw dataset separate from the source code. Do not commit large datasets to Git unless their size and redistribution permissions have been checked.

---

## 4. Project Scope

### Phase 1 — Data Engineering

Implement the preprocessing pipeline in ordinary Python modules.

Responsibilities:

- Load CSV data.
- Validate required columns and data types.
- Detect duplicate identifiers.
- Handle missing and invalid values.
- Validate numerical metrics.
- Document cleaning decisions.
- Provide a consistent data interface to the application.

**Deliverable:** A reusable, tested data-loading and preprocessing module.

### Phase 2 — Analytical Engine

Implement independent Python functions for:

- Summary statistics.
- Metric distributions.
- Top-anime rankings.
- Genre-level aggregation.
- Type-level comparisons.
- Rating and engagement comparisons.
- Pareto and decile analysis.

Analytical functions must remain independent of HTTP request handling so they can be tested and reused without starting the API server.

**Deliverable:** A modular analytical engine.

### Phase 3 — FastAPI Application

Expose the analytical functions through REST endpoints.

The application should support:

- Anime lookup by identifier.
- Filtering by genre and type.
- Sorting by supported metrics.
- Pagination.
- Descriptive statistics.
- Genre summaries.
- Metric distribution analysis.
- Pareto analysis.

**Deliverable:** A functioning REST API with validated inputs and documented responses.

### Phase 4 — Testing and Reliability

- Unit-test preprocessing and analytical functions.
- Test API routes with HTTPX and FastAPI's test client.
- Validate input constraints.
- Test missing identifiers and unsupported metrics.
- Test Pareto grouping with duplicate values.
- Handle empty datasets and zero-total metrics.
- Verify that API responses follow their documented schemas.

**Deliverable:** An automated test suite with reproducible execution instructions.

### Phase 5 — Deployment Readiness

- Add structured application logging.
- Configure environment-specific settings.
- Add a health-check endpoint.
- Configure dependency management.
- Add Docker support as an optional extension.
- Add CI using GitHub Actions as an optional extension.

**Deliverable:** A repository ready for repeatable execution and deployment.

---

## 5. Pareto and Decile Analysis

### Objective

Determine how much of the total value of a selected metric is contributed by different equally sized groups of anime.

For example:

- What proportion of total completions is associated with the highest-ranked 10% of anime?
- How concentrated are favorites among the most-engaged titles?
- Does membership show the same concentration pattern as completion counts?
- How do results change when the number of groups changes?

### Required function

```python
def pareto_analysis(
    metric_column: str,
    n: int = 10,
) -> pd.Series:
    ...
```

The function will operate on the cleaned dataset supplied by the application or its calling service.

### Analytical requirements

1. Sort observations by the selected metric in descending order.
2. Rank values using `rank(method="first")` to handle ties.
3. Use `pd.qcut()` on the ranks to divide the observations into `n` approximately equal-sized groups.
4. Calculate each group's sum as a proportion of the overall metric total.
5. Sort the resulting proportions in descending order.
6. Label the output `Group 1` through `Group n`.
7. Return a Pandas Series.

### Expected result

```text
Group 1    0.94...
Group 2    0.04...
Group 3    0.01...
Group 4    0.00...
Group 5    0.00...
dtype: float64
```

The values above are illustrative, not measured results.

### Important constraints

- Validate the requested metric.
- Require a positive integer for `n`.
- Handle insufficient observations.
- Define behavior for missing and negative metric values.
- Prevent division by zero.
- Verify that the group proportions sum to approximately `1.0` when the total is positive.

The analysis must not assume that every dataset follows the 80/20 rule. That conclusion must be evaluated from the actual results.

---

## 6. API Specification

The following endpoints define the planned interface.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/anime` | Retrieve filtered and paginated anime |
| `GET` | `/anime/{mal_id}` | Retrieve one anime |
| `GET` | `/analytics/overview` | Summary statistics |
| `GET` | `/analytics/top-anime` | Rank anime by a supported metric |
| `GET` | `/analytics/genres` | Aggregate metrics by genre |
| `GET` | `/analytics/distribution/{metric}` | Analyze metric distributions |
| `GET` | `/analytics/pareto` | Calculate ranked group proportions |

### Example requests

Retrieve the first 20 anime:

```http
GET /anime?limit=20&offset=0
```

Filter anime by type:

```http
GET /anime?anime_type=TV&limit=20
```

Retrieve anime by MAL identifier:

```http
GET /anime/1
```

Rank anime by members:

```http
GET /analytics/top-anime?metric=Members&limit=10
```

Perform decile analysis:

```http
GET /analytics/pareto?metric=Completed&n=10
```

Interactive documentation will be available at:

```text
/docs
```

The final endpoint parameters and response schemas must match the implemented code.

---

## 7. Example API Response

An illustrative Pareto response could look like this:

```json
{
  "metric": "Completed",
  "groups": 5,
  "results": [
    {"group": "Group 1", "proportion": 0.94},
    {"group": "Group 2", "proportion": 0.04},
    {"group": "Group 3", "proportion": 0.01},
    {"group": "Group 4", "proportion": 0.006},
    {"group": "Group 5", "proportion": 0.004}
  ]
}
```

The numbers are placeholders. Actual values must be calculated from the dataset.

---

## 8. Architecture

The application will follow a layered architecture.

```text
Client
  |
  v
FastAPI Routes
  |
  v
Request Validation and Response Schemas
  |
  v
Service Layer
  |
  +-------------------+
  |                   |
  v                   v
Anime Repository   Analytics Engine
  |                   |
  v                   v
Cleaned Dataset   Statistical Functions
```

### Architectural responsibilities

- **API routes:** Handle HTTP requests and responses.
- **Schemas:** Validate inputs and define response structures.
- **Services:** Coordinate application operations.
- **Repository:** Provide access to the loaded anime data.
- **Analytics engine:** Execute statistical and analytical functions.
- **Preprocessing:** Validate and clean source data.
- **Tests:** Verify expected behavior independently of production data.

This separation prevents analytical logic from becoming tightly coupled to individual endpoints.

---

## 9. Repository Structure

The repository will use a modular Python package with no notebook directory.

```text
anime-analytics-api/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── pyproject.toml
├── uv.lock
│
├── data/
│   └── README.md
│
├── src/
│   └── anime_analytics/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── anime.py
│       │       └── analytics.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── anime.py
│       │   └── analytics.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── anime_service.py
│       │   └── analytics_service.py
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   └── anime_repository.py
│       │
│       └── analytics/
│           ├── __init__.py
│           ├── preprocessing.py
│           ├── descriptive.py
│           ├── aggregation.py
│           └── pareto.py
│
├── tests/
│   ├── conftest.py
│   ├── test_preprocessing.py
│   ├── test_anime_api.py
│   ├── test_analytics.py
│   └── test_pareto.py
│
└── docs/
    ├── architecture.md
    ├── data_dictionary.md
    └── analytical_methodology.md
```

### Structure principles

- No Jupyter notebooks.
- No business logic inside the README.
- No unnecessary abstractions for a small initial application.
- Keep functions small, typed, testable, and reusable.
- Use synthetic fixtures for tests instead of depending entirely on the full dataset.
- Introduce a database only if the requirements justify it.

---

## 10. Technology Stack

| Technology | Responsibility |
|---|---|
| Python 3.11+ | Application language |
| Pandas | Data transformation and aggregation |
| NumPy | Numerical computation |
| FastAPI | REST API framework |
| Pydantic | Validation and serialization |
| Uvicorn | ASGI server |
| Pytest | Automated testing |
| HTTPX | API integration testing |
| Ruff | Linting and formatting |
| Mypy | Static type checking |
| Git | Version control |
| GitHub Actions | Optional continuous integration |
| Docker | Optional containerization |

Use a compatible, locked dependency set rather than assuming every latest package version will work together.

---

## 11. Setup and Execution

### Prerequisites

- Python 3.11 or a compatible supported version.
- Git.
- A local copy of the anime metadata CSV.
- A virtual environment or dependency manager.

### Install dependencies

If using `pip`:

```bash
pip install fastapi uvicorn pandas numpy pydantic pytest httpx
```

### Start the API

From the project root, after implementing the application entry point:

```bash
uvicorn anime_analytics.main:app --reload --app-dir src
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Run tests

```bash
pytest -v
```

### Run code-quality checks

After configuring Ruff and Mypy:

```bash
ruff check .
ruff format --check .
mypy src/
```

These commands are intended for the completed implementation. The project configuration and package installation must be set up before all commands will work.

---

## 12. Functional Requirements

### Data engineering

- [ ] Load and validate the source CSV.
- [ ] Validate required columns and data types.
- [ ] Document missing-value policies.
- [ ] Detect duplicate identifiers.
- [ ] Handle invalid metric values.
- [ ] Keep raw data separate from application code.

### Analytical engine

- [ ] Implement descriptive statistics.
- [ ] Implement top-anime rankings.
- [ ] Implement genre-level aggregations.
- [ ] Implement type-level comparisons.
- [ ] Implement metric distribution analysis.
- [ ] Implement generalized Pareto analysis.
- [ ] Test ties, missing values, and zero-total cases.

### API engineering

- [ ] Implement anime retrieval and identifier lookup.
- [ ] Implement filtering and pagination.
- [ ] Implement analytics endpoints.
- [ ] Define request and response schemas.
- [ ] Return appropriate HTTP status codes.
- [ ] Generate accurate OpenAPI documentation.

### Quality assurance

- [ ] Write unit tests.
- [ ] Write API integration tests.
- [ ] Configure structured logging.
- [ ] Add type hints.
- [ ] Configure linting and formatting.
- [ ] Document setup and execution.

---

## 13. Non-Functional Requirements

### Reliability

The API must validate user inputs and return predictable errors rather than exposing unhandled exceptions.

### Maintainability

Routes, analytical functions, preprocessing, and data access must remain separated.

### Performance

The initial implementation should load and preprocess the dataset efficiently, avoid unnecessary repeated CSV reads, and paginate large responses.

### Reproducibility

Data-cleaning rules, dependency versions, analytical assumptions, and test procedures must be documented.

### Security

Do not expose local filesystem paths, stack traces, credentials, or sensitive configuration through API responses.

### Interpretability

Statistical results should be accompanied by clear metric definitions and limitations.

---

## 14. Engineering Constraints

1. Popularity is a rank; members and completions are counts. Do not interpret them as equivalent quantities.
2. Document the treatment of missing and invalid metric values.
3. Reject unsupported metric names and invalid group counts.
4. Do not silently modify the source dataset.
5. Prevent division by zero in proportion calculations.
6. Do not infer causation from correlations.
7. Do not claim that the dataset measures current streaming viewership.
8. Avoid loading additional large CSV files until they are needed.
9. Keep generated artifacts and large source files out of version control when appropriate.
10. Do not claim deployment, test coverage, or production readiness without evidence.

---

## 15. Definition of Done

The project is complete when:

- The application starts from a clean environment.
- The dataset is loaded and validated using documented rules.
- All required endpoints work as specified.
- Pareto analysis produces mathematically valid results.
- Invalid inputs are handled consistently.
- Automated tests pass.
- Code-quality checks run successfully.
- API documentation reflects actual behavior.
- Another developer can reproduce the application using the README.

---

## 16. Future Extensions

Possible extensions include:

- PostgreSQL integration.
- SQLAlchemy-based persistence.
- Content-based anime recommendation.
- Synopsis similarity analysis.
- Genre and studio benchmarking.
- Interactive frontend development.
- Docker deployment.
- GitHub Actions CI.
- API performance benchmarking.
- Data-quality monitoring.

These extensions are optional and should be added only after the core application is stable.

---

## 17. Dataset Attribution

The project uses the MyAnimeList Database 2020 dataset.

- [Original repository](https://github.com/Hernan4444/MyAnimelist-Database)
- [Kaggle dataset](https://www.kaggle.com/datasets/hernan4444/anime-recommendation-database-2020)

Review the original source terms and applicable permissions before redistributing dataset files. Clearly distinguish third-party data from original code and analysis.

---

## Project Summary

Anime Analytics API is a code-first data analytics project that combines Python, Pandas, statistical analysis, and FastAPI.

It demonstrates how to transform structured data into reusable analytical functions and expose those functions through a documented REST API.

The project prioritizes modular architecture, reproducibility, automated testing, analytical correctness, and maintainable Python code.

**Current status:** In development.

**Primary goal:** Build a well-tested anime analytics service that can be extended into a production-style backend application.