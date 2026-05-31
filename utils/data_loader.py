import pandas as pd
import json
import os

def load_data():
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to backend/data directory
    data_dir = os.path.join(current_dir, "..", "data")
    
    stations = pd.read_csv(os.path.join(data_dir, "stations.csv"))
    edges = pd.read_csv(os.path.join(data_dir, "edges.csv"))

    with open(os.path.join(data_dir, "fare_rules.json")) as f:
        fare_rules = json.load(f)

    return stations, edges, fare_rules