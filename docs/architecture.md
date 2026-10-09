# Architecture

```text
Client
  |
  v
FastAPI routes            api/routes/{anime,analytics}.py
  |   validate query/path parameters, map errors to HTTP
  v
Services                  services/{anime,analytics}_service.py
  |   turn results into response schemas
  +--------------------+
  |                    |
  v                    v
Repository             Analytics functions
repositories/          analytics/{descriptive,ranking,aggregation,
anime_repository.py              distribution,engagement,pareto}.py
  |
  v
Preprocessing          analytics/preprocessing.py
  |
  v
anime.csv (read once at startup)
```

## Layers

| Layer | Responsibility | Knows about HTTP? |
|---|---|---|
| `api/routes` | Parameter validation (types, ranges, allowed metric names), status codes | yes |
| `api/dependencies.py` | Supplies the repository and services to routes | yes |
| `schemas` | Pydantic response models (also the OpenAPI contract) | no |
| `services` | Combine repository data and analytics into response schemas | no |
| `repositories` | Load the CSV once; lookup, filter, sort, paginate | no |
| `analytics` | Pure functions on DataFrames: no I/O, no globals | no |
| `config.py` | Settings from environment / `.env` | no |
| `exceptions.py` | `DatasetError`, `AnalysisError`, `DatasetUnavailableError` | no |

Analytical functions take a DataFrame and return plain Python or pandas
objects, so they are tested with small synthetic frames and could be reused
from a script or notebook.

## Data flow and state

- `create_app()` builds the application. At startup (the FastAPI lifespan) it
  calls `AnimeRepository.from_csv()`, which reads the CSV as text, cleans it
  and keeps only the cleaned table in memory. Requests never read the file.
- The repository is stored on `app.state`, not in a module-level global.
  Tests pass in a repository built from synthetic data.
- The cleaned table is shared between requests and treated as read-only. Every
  analytical function works on copies or new Series; tests assert the table is
  unchanged after each endpoint runs.
- If loading fails the app still starts. `/health` reports `degraded` and data
  endpoints answer `503` with a generic message (no filesystem paths in
  responses; details go to the log).

## Error mapping

| Situation | Status |
|---|---|
| Invalid or unsupported parameter (wrong type, out of range, unsupported metric or sort field) | 422 (FastAPI validation) |
| Valid parameters but the analysis cannot be performed (`AnalysisError`, e.g. more Pareto groups than observations) | 400 |
| Unknown `mal_id` | 404 |
| Dataset not loaded | 503 |

All error bodies have the shape `{"detail": ...}`.

## Why this shape

- The analytics package has no dependency on FastAPI, which keeps statistical
  logic testable and reusable.
- A metric registry (`analytics/metrics.py`) is the single list of columns the
  API exposes, so callers cannot pass arbitrary column names to the analytics
  code. Tests check that the `Literal` types used for OpenAPI enums stay in
  sync with it.
- No database: the dataset is small (about 6 MB, 17k rows) and read-only.
