import networkx as nx
import random
import math

def generate_grid_graph(rows=4, cols=5, spacing=1.0, speed=40.0):
    """Generate a grid-style logistics graph with nodes and realistic travel attributes."""
    G = nx.Graph()
    node_id = 0
    positions = {}

    for r in range(rows):
        for c in range(cols):
            positions[node_id] = (c * spacing, r * spacing)
            G.add_node(node_id, pos=positions[node_id], name=f"Location {node_id}")
            node_id += 1

    def euclid(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    for i in G.nodes:
        for j in G.nodes:
            if i >= j:
                continue
            a = positions[i]
            b = positions[j]
            if abs(a[0] - b[0]) <= spacing + 1e-6 and abs(a[1] - b[1]) <= spacing + 1e-6:
                distance = euclid(a, b)
                base_time = distance / speed * 60.0
                variation = random.uniform(0.9, 1.15)
                travel_time = base_time * variation
                G.add_edge(
                    i,
                    j,
                    distance=round(distance, 3),
                    time=round(travel_time, 3),
                    base_time=round(base_time, 3),
                    road_quality=random.choice(["good", "fair", "poor"]),
                )

    return G

def sample_graph():
    return generate_grid_graph(rows=4, cols=5, spacing=1.0, speed=40.0)
