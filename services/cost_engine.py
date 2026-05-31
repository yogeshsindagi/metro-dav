from utils.data_loader import load_data
from utils.graph import build_graph, shortest_path_info
from utils.fare import compute_fare

stations_df, edges_df, fare_rules = load_data()
graph = build_graph(edges_df)


def compute_route(source, destination, last_mile):
    dist_hops = shortest_path_info(graph, source, destination)

    if dist_hops == (None, None):
        return None
        
    distance, hops = dist_hops

    metro_fare = compute_fare(hops)
    metro_cost = metro_fare + (last_mile * 20 * 2)

    total_car_distance = distance + (last_mile * 2)
    car_cost = total_car_distance * 10 + 50

    winner = "metro" if metro_cost < car_cost else "car"

    return {
        "distance_km": round(total_car_distance, 2),
        "metro_cost": round(metro_cost, 2),
        "car_cost": round(car_cost, 2),
        "winner": winner
    }


def generate_matrix(last_mile):
    results = []

    stations = list(graph.keys())

    for src in stations:
        for dest in stations:
            if src == dest:
                continue

            result = compute_route(src, dest, last_mile)

            if result is None:
                continue

            results.append({
                "source": src,
                "destination": dest,
                **result
            })

    return {
        "total_routes": len(results),
        "data": results
    }

def compute_threshold(source, destination):
    dist_hops = shortest_path_info(graph, source, destination)

    if dist_hops == (None, None):
        return None
        
    distance, hops = dist_hops

    metro_fare = compute_fare(hops)

    car_base = distance * 10 + 50
    threshold = (car_base - metro_fare) / 20.0

    return round(max(threshold, 0), 2)
def compute_station_zone(source):
    max_distance = 10  # km range we check
    step = 0.1

    best_zone = 0

    stations = list(graph.keys())

    for last_mile in [i * step for i in range(int(max_distance / step))]:
        metro_better_count = 0
        total = 0

        for dest in stations:
            if source == dest:
                continue

            dist_hops = shortest_path_info(graph, source, dest)
            if dist_hops == (None, None):
                continue
                
            distance, hops = dist_hops

            metro_fare = compute_fare(hops)
            metro_cost = metro_fare + (last_mile * 20 * 2)

            total_car_distance = distance + (last_mile * 2)
            car_cost = total_car_distance * 10 + 50

            total += 1
            if metro_cost < car_cost:
                metro_better_count += 1

        # 👉 If metro wins majority → viable zone
        if total > 0 and metro_better_count / total >= 0.5:
            best_zone = last_mile

    return round(best_zone, 2)