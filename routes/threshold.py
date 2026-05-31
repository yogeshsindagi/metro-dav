from fastapi import APIRouter
from services.cost_engine import compute_threshold

router = APIRouter()

@router.get("/threshold")
def get_threshold(source: str, destination: str):
    threshold = compute_threshold(source, destination)

    if threshold is None:
        return {"error": "Invalid route"}

    return {
        "source": source,
        "destination": destination,
        "threshold_km": threshold
    }