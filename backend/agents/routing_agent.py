import networkx as nx
from typing import List, Dict

class RoutingAgent:
    """Computes optimal path using NetworkX on a weighted graph."""
    def __init__(self, graph):
        self.graph = graph

    def shortest_path_by_time(self, source: int, target: int) -> Dict:
        try:
            path = nx.shortest_path(self.graph, source=source, target=target, weight='time')
            length_time = nx.path_weight(self.graph, path, weight='time')
            length_dist = nx.path_weight(self.graph, path, weight='distance')
            return {"path": path, "time": round(length_time, 3), "distance": round(length_dist, 3)}
        except Exception as e:
            return {"error": str(e)}

    def k_shortest_paths_by_time(self, source: int, target: int, k: int = 3) -> List[Dict]:
        results = []
        G = self.graph
        primary = self.shortest_path_by_time(source, target)
        if 'error' in primary:
            return [primary]
        results.append(primary)
        for u, v in zip(primary['path'][:-1], primary['path'][1:]):
            original = G[u][v].get('time', 1.0)
            G[u][v]['time'] = original * 5.0
            alt = self.shortest_path_by_time(source, target)
            if 'path' in alt and alt not in results:
                results.append(alt)
            G[u][v]['time'] = original
            if len(results) >= k:
                break
        return results

    def route_summary(self, route: Dict) -> Dict:
        if 'error' in route:
            return route
        return {
            "path": route['path'],
            "time": route['time'],
            "distance": route['distance'],
            "segments": len(route['path']) - 1,
        }
