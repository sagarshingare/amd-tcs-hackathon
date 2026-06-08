from typing import Dict, Any

class DisruptionAgent:
    """Detects anomalies and marks graph edges as disrupted."""
    def __init__(self, graph):
        self.graph = graph
        self.disrupted_edges = {}

    def apply_traffic_disruption(self, edge, severity: float):
        a, b = edge
        if self.graph.has_edge(a, b):
            base = self.graph[a][b].get("base_time", self.graph[a][b].get("time", 1.0))
            new_time = base * severity
            self.graph[a][b]["time"] = new_time
            self.disrupted_edges[(a, b)] = {"type": "traffic", "severity": severity, "new_time": new_time}
            return True
        return False

    def apply_fuel_change(self, new_price: float):
        # fuel price is managed by MonitoringAgent and CostAgent; here we record it
        self.latest_fuel_price = new_price
        return True

    def clear_disruptions(self):
        # Restore base_time to time for disrupted edges
        for (a, b), info in list(self.disrupted_edges.items()):
            if self.graph.has_edge(a, b):
                self.graph[a][b]["time"] = self.graph[a][b].get("base_time", self.graph[a][b]["time"])
        self.disrupted_edges = {}
