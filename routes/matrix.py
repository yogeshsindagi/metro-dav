from fastapi import APIRouter
from services.cost_engine import generate_matrix

router = APIRouter()

@router.get("/matrix")
def matrix(last_mile_km: float):
    return generate_matrix(last_mile_km)