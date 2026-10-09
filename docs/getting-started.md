
# Getting Started

## Prerequisites

- Python 3.11 or newer.
- Git.
- The MyAnimeList Database 2020 `anime.csv` file.
- A terminal and code editor.

## 1. Clone the repository

```powershell
git clone https://github.com/sunilnarayan419-ui/Anime-Analytics-API.git
cd Anime-Analytics-API
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 4. Obtain the dataset

The CSV is excluded from the repository.

Create the data directory if necessary:

```powershell
New-Item -ItemType Directory -Force data
```

Download the dataset:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/Hernan4444/MyAnimelist-Database/master/data/anime.csv" `
  -OutFile "data/anime.csv"
```

Alternatively, obtain the dataset from the original source or Kaggle and place it at `data/anime.csv`.

Review the source's terms before redistributing the dataset.

## 5. Configure the application

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

The default configuration expects the dataset at `data/anime.csv`.

Available settings are documented in `.env.example` and the project's README.

## 6. Run the API

```powershell
uvicorn anime_analytics.main:app --app-dir src --reload
```

Open:

- API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Health endpoint: http://127.0.0.1:8000/health

## 7. Verify the dataset

Check the health endpoint and confirm that the dataset is loaded.

If the dataset is unavailable, the application can start in a degraded state. Data-dependent endpoints return an appropriate service-unavailable response.

## Troubleshooting

### Module not found

Activate the virtual environment and run:

```bash
pip install -e ".[dev]"
```

### Dataset not found

Verify that `data/anime.csv` exists or configure `DATA_PATH` to point to the dataset.

### Port already in use

Stop the process using port 8000 or configure Uvicorn to use another port.

For the complete endpoint list, see the [API Reference](api-reference.md).
