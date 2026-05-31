from routes.compare import compare
from pydantic import BaseModel

class Car(BaseModel):
    mileage: float = 15.0
    fuel_price: float = 100.0
    extra_cost: float = 0

class Req(BaseModel):
    source: str = 'Pattanagere'
    destination: str = 'Nayandahalli'
    last_mile_km: float = 2.0
    car_config: Car = Car()

print(compare(Req()))
