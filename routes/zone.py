from fastapi import APIRouter
from services.cost_engine import compute_station_zone

router = APIRouter()

@router.get("/zone")
def zone(source: str):
    result = compute_station_zone(source)

    if result is None:
        return {"error": "Invalid station"}

    return {
        "source": source,
        "metro_win_zone_km": result
    }