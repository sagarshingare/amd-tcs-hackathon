import networkx as nx
import random
import math

def generate_grid_graph(rows=3, cols=4, spacing=1.0, speed=40.0):
    """Generates a grid-like graph with positions and edge attributes.

    Returns: Graph with node positions, edges have distance and travel_time.
    """
    G = nx.Graph()
    node_id = 0
    positions = {}
    for r in range(rows):
        for c in range(cols):
            G.add_node(node_id)
            positions[node_id] = (c * spacing, r * spacing)
            node_id += 1

    def euclid(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    for i in G.nodes:
        x1 = positions[i]
        for j in G.nodes:
            if i >= j:
                continue
            x2 = positions[j]
            # connect near neighbors only (grid connectivity)
            if abs(x1[0] - x2[0]) <= spacing + 1e-6 and abs(x1[1] - x2[1]) <= spacing + 1e-6:
                d = euclid(x1, x2)
                travel_time = d / speed * 60.0  # minutes
                G.add_edge(i, j, distance=d, time=travel_time, base_time=travel_time)

    nx.set_node_attributes(G, positions, "pos")
    return G

def sample_graph():
    return generate_grid_graph(rows=4, cols=5, spacing=1.0, speed=40.0)
