from utils.data_loader import load_data
from utils.graph import build_graph, shortest_distance
from utils.fare import compute_fare

stations_df, edges_df, fare_rules = load_data()
graph = build_graph(edges_df)


def compute_route(source, destination, last_mile):
    distance = shortest_distance(graph, source, destination)

    if distance is None:
        return None

    metro_fare = compute_fare(distance, fare_rules)
    metro_cost = metro_fare + (last_mile * 20 * 2)

    car_cost = distance * 10 + 50

    winner = "metro" if metro_cost < car_cost else "car"

    return {
        "distance_km": round(distance, 2),
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
    distance = shortest_distance(graph, source, destination)

    if distance is None:
        return None

    metro_fare = compute_fare(distance, fare_rules)

    car_cost = distance * 10 + 50
    auto_rate = 20

    threshold = (car_cost - metro_fare) / (2 * auto_rate)

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

            distance = shortest_distance(graph, source, dest)
            if distance is None:
                continue

            metro_fare = compute_fare(distance, fare_rules)
            metro_cost = metro_fare + (last_mile * 20 * 2)

            car_cost = distance * 10 + 50

            total += 1
            if metro_cost < car_cost:
                metro_better_count += 1

        # 👉 If metro wins majority → viable zone
        if total > 0 and metro_better_count / total >= 0.5:
            best_zone = last_mile

    return round(best_zone, 2)