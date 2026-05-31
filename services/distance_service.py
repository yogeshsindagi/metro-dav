import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_distance(origin, destination):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json",
    }

    body = {
        "coordinates": [
            [origin["lng"], origin["lat"]],
            [destination["lng"], destination["lat"]],
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    try:
        distance_m = data["routes"][0]["summary"]["distance"]
        return distance_m / 1000  # meters → km
    except:
        return None