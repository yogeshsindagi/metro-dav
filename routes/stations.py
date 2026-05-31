from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate to backend/data directory
data_dir = os.path.join(current_dir, "..", "data")

stations_df = pd.read_csv(os.path.join(data_dir, "stations.csv"))

@router.get("/stations")
def get_stations():
    return stations_df.to_dict(orient="records")