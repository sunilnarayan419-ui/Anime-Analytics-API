
# Anime Analytics API

A documented, tested REST API for exploring anime metadata and performing statistical analysis using Python, Pandas, NumPy and FastAPI.

[![CI](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml/badge.svg)](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions/workflows/ci.yml)

## What this project does

The Anime Analytics API provides programmatic access to anime metadata, filtering, ranking and aggregate statistical analysis.

### Key capabilities

- Search, filter, sort and paginate anime records.
- Retrieve individual anime by MyAnimeList ID.
- Examine dataset statistics and data-quality information.
- Rank anime using supported metrics.
- Compare genres and anime types.
- Analyze engagement metrics and metric distributions.
- Investigate concentration using Pareto/decile analysis.

## Explore the documentation

- [Getting Started](getting-started.md)
- [API Reference](api-reference.md)
- [Architecture](architecture.md)
- [Analytical Methodology](analytical_methodology.md)
- [Data Dictionary](data_dictionary.md)
- [Development and Testing](development.md)

## Quick links

- [Interactive API documentation](http://127.0.0.1:8000/docs) — available when running locally.
- [GitHub repository](https://github.com/sunilnarayan419-ui/Anime-Analytics-API)
- [GitHub Actions CI](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions)

## Dataset

The application uses the MyAnimeList Database 2020 dataset. The CSV is not included in this repository and must be obtained separately.

See [Getting Started](getting-started.md) for setup instructions.

## Scope and limitations

This project analyzes a historical dataset, not live MyAnimeList data. Recorded membership and completion counts represent platform list entries rather than verified unique viewers or streams.

Read the [analytical methodology](analytical_methodology.md) before interpreting the results.
