import heapq

def build_graph(edges_df):
    graph = {}

    for _, row in edges_df.iterrows():
        u = row["from_station"]
        v = row["to_station"]
        d = row["distance_km"]

        graph.setdefault(u, []).append((v, d))
        graph.setdefault(v, []).append((u, d))  # undirected

    return graph


def shortest_distance(graph, start, end):
    pq = [(0, start)]
    visited = set()

    while pq:
        dist, node = heapq.heappop(pq)

        if node == end:
            return dist

        if node in visited:
            continue

        visited.add(node)

        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (dist + weight, neighbor))

    return None  # no path