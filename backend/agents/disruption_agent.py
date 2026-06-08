from typing import Dict, Any

class DisruptionAgent:
    """Detects anomalies and marks graph edges as disrupted."""
    def __init__(self, graph):
        self.graph = graph
        self.disrupted_edges = {}
        self.latest_fuel_price = None

    def apply_traffic_disruption(self, edge, severity: float):
        a, b = edge
        if self.graph.has_edge(a, b):
            base = self.graph[a][b].get("base_time", self.graph[a][b].get("time", 1.0))
            new_time = round(base * severity, 3)
            self.graph[a][b]["time"] = new_time
            self.disrupted_edges[(a, b)] = {
                "type": "traffic",
                "severity": severity,
                "new_time": new_time,
                "description": "Traffic delay increased travel time",
            }
            return True
        return False

    def apply_weather_disruption(self, edge, severity: float, weather: str):
        a, b = edge
        if self.graph.has_edge(a, b):
            base = self.graph[a][b].get("base_time", self.graph[a][b].get("time", 1.0))
            multiplier = 1.1 + severity * 0.4
            new_time = round(base * multiplier, 3)
            self.graph[a][b]["time"] = new_time
            self.disrupted_edges[(a, b)] = {
                "type": "weather",
                "weather": weather,
                "severity": severity,
                "new_time": new_time,
                "description": f"{weather.title()} slows traffic on the segment",
            }
            return True
        return False

    def apply_fuel_change(self, new_price: float):
        self.latest_fuel_price = new_price
        return True

    def clear_disruptions(self):
        for (a, b), info in list(self.disrupted_edges.items()):
            if self.graph.has_edge(a, b):
                self.graph[a][b]["time"] = self.graph[a][b].get("base_time", self.graph[a][b]["time"])
        self.disrupted_edges = {}
