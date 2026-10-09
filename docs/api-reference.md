
# API Reference

The API exposes read-only endpoints for anime lookup and analytics.

When the application is running locally, explore interactive request schemas at:

[Swagger UI](http://127.0.0.1:8000/docs)

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health and dataset status |
| GET | `/anime` | Filtering, sorting and pagination |
| GET | `/anime/{mal_id}` | Retrieve anime by ID |
| GET | `/analytics/overview` | Dataset summary and data quality |
| GET | `/analytics/top-anime` | Rank anime by a metric |
| GET | `/analytics/genres` | Aggregate metrics by genre |
| GET | `/analytics/types` | Compare anime types |
| GET | `/analytics/engagement` | Analyze engagement rates |
| GET | `/analytics/distribution/{metric}` | Metric distributions |
| GET | `/analytics/pareto` | Pareto/decile concentration analysis |

## Example requests

### List anime

```http
GET /anime?limit=5&offset=0
```

Returns pagination metadata and a list of anime records.

### Filter anime

```http
GET /anime?genre=Action&anime_type=TV&min_score=8&limit=5
```

Filters are combined using AND.

### Rank anime

```http
GET /analytics/top-anime?metric=Members&limit=10
```

Ranks titles using the selected metric.

### Analyze metric distribution

```http
GET /analytics/distribution/Score?bins=10
```

Returns descriptive statistics, percentiles and histogram information.

### Analyze concentration

```http
GET /analytics/pareto?metric=Completed&n=10
```

Divides ranked observations into groups and reports their shares of the selected metric.

## Validation and errors

| Status | Meaning |
|---|---|
| 400 | The requested analysis cannot be performed |
| 404 | Anime ID not found |
| 422 | Invalid parameters or unsupported values |
| 503 | Dataset unavailable |

See [Analytical Methodology](analytical_methodology.md) for metric definitions and assumptions.
