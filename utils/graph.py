import heapq

def build_graph(edges_df):
    graph = {}
    has_hops = "hop_count" in edges_df.columns

    for _, row in edges_df.iterrows():
        u = row["from_station"]
        v = row["to_station"]
        d = row["distance_km"]
        h = row["hop_count"] if has_hops else 1

        graph.setdefault(u, []).append((v, d, h))
        graph.setdefault(v, []).append((u, d, h))  # undirected

    return graph


def shortest_path_info(graph, start, end):
    pq = [(0, 0, start)] # (distance, hops, node)
    visited = set()

    while pq:
        dist, hops, node = heapq.heappop(pq)

        if node == end:
            return dist, hops

        if node in visited:
            continue

        visited.add(node)

        for neighbor, weight_d, weight_h in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (dist + weight_d, hops + weight_h, neighbor))

    return None, None