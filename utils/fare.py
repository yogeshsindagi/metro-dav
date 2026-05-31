def compute_fare(distance, rules):
    fare = rules["base_fare"] + distance * rules["per_km"]
    return min(fare, rules["max_fare"])