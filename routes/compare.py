from fastapi import APIRouter
from pydantic import BaseModel

from utils.data_loader import load_data
from utils.graph import build_graph, shortest_path_info
from utils.fare import compute_fare

from services.car_model import compute_car_cost
from services.distance_service import get_distance as get_road_distance
from services.geocoding_service import geocode_address

router = APIRouter()

# Load data
stations_df, edges_df, fare_rules = load_data()
graph = build_graph(edges_df)


# -----------------------------
# REQUEST MODEL
# -----------------------------
class CarConfig(BaseModel):
    mileage: float
    fuel_price: float
    extra_cost: float = 0


class CompareRequest(BaseModel):
    source: str
    destination: str
    last_mile_km: float
    car_config: CarConfig


# -----------------------------
# HELPER → get lat/lng
# -----------------------------
def get_station_coords(name):
    row = stations_df[stations_df["station_name"] == name]

    if row.empty:
        return None

    return {
        "lat": float(row.iloc[0]["lat"]),
        "lng": float(row.iloc[0]["lng"]),
    }


# -----------------------------
# MAIN API
# -----------------------------
@router.post("/compare")
def compare(req: CompareRequest):
    source = req.source
    destination = req.destination

    # 🚫 invalid same station
    if source == destination:
        return {"error": "Same source and destination"}

    # -------------------------
    # METRO DISTANCE (GRAPH)
    # -------------------------
    dist_hops = shortest_path_info(graph, source, destination)

    if dist_hops == (None, None):
        return {"error": "Invalid route"}

    metro_distance, hops = dist_hops
    metro_fare = compute_fare(hops)

    # -------------------------
    # LAST MILE COST (Simple calculation)
    # -------------------------
    # Use simple rate-based calculation for last-mile cost
    # Default: ₹20 per km (auto/taxi rate)
    last_mile_cost = req.last_mile_km * 20

    # Total metro cost is metro fare + last-mile cost
    metro_cost = metro_fare + last_mile_cost

    # -------------------------
    # ROAD DISTANCE (API)
    # -------------------------
    origin = get_station_coords(source)
    dest = get_station_coords(destination)

    road_distance = None

    if origin and dest:
        road_distance = get_road_distance(origin, dest)

    # 🔥 fallback (VERY IMPORTANT)
    if road_distance is None:
        road_distance = metro_distance

    # -------------------------
    # CAR COST (USER CONFIG)
    # -------------------------
    car_cost = compute_car_cost(
        distance_km=road_distance,
        mileage=req.car_config.mileage,
        fuel_price=req.car_config.fuel_price,
        extra_cost=req.car_config.extra_cost,
    )

    # -------------------------
    # RESULT
    # -------------------------
    winner = "metro" if metro_cost < car_cost else "car"

    return {
        "distance_km": round(road_distance, 2),
        "metro_cost": round(metro_cost, 2),
        "car_cost": car_cost,
        "winner": winner,
    }