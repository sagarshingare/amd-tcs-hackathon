import networkx as nx
from typing import List, Tuple, Dict

class RoutingAgent:
    """Computes optimal path using NetworkX on a weighted graph."""
    def __init__(self, graph):
        self.graph = graph

    def shortest_path_by_time(self, source: int, target: int) -> Dict:
        try:
            path = nx.shortest_path(self.graph, source=source, target=target, weight='time')
            length_time = nx.path_weight(self.graph, path, weight='time')
            length_dist = nx.path_weight(self.graph, path, weight='distance')
            return {"path": path, "time": length_time, "distance": length_dist}
        except Exception as e:
            return {"error": str(e)}

    def k_shortest_paths_by_time(self, source: int, target: int, k: int = 3) -> List[Dict]:
        # simple fallback: use shortest_path, then try removing edges to get alternatives
        results = []
        G = self.graph
        try:
            primary = self.shortest_path_by_time(source, target)
            results.append(primary)
            # attempt simple alternatives by temporarily increasing weights on edges in primary
            for edge in zip(primary['path'][:-1], primary['path'][1:]):
                u, v = edge
                original = G[u][v].get('time', 1.0)
                G[u][v]['time'] = original * 5.0
                alt = self.shortest_path_by_time(source, target)
                if 'path' in alt and alt not in results:
                    results.append(alt)
                G[u][v]['time'] = original
                if len(results) >= k:
                    break
        except Exception:
            pass
        return results
