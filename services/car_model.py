def compute_car_cost(
    distance_km: float,
    mileage: float,
    fuel_price: float,
    extra_cost: float = 0,
    wear_rate: float = 2.5,  # ₹ per km
):
    if mileage <= 0:
        return None

    fuel_cost = (distance_km / mileage) * fuel_price
    wear_cost = distance_km * wear_rate

    total = fuel_cost + wear_cost + extra_cost

    return round(total, 2)
