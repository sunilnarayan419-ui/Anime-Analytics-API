from fastapi import APIRouter, HTTPException, Query

from anime_analytics.services.analytics_service import run_pareto_analysis

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/pareto")
def pareto_analysis(
    metric: str = Query(
        ...,
        description="Numeric dataset column, e.g. Completed or Members",
    ),
    n: int = Query(10, ge=1, description="Number of groups"),
) -> dict:
    try:
        result = run_pareto_analysis(metric, n)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "metric": metric,
        "groups": n,
        "results": [
            {"group": str(group), "proportion": float(value)}
            for group, value in result.items()
        ],
    }
