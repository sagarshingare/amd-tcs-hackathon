import random
from typing import Dict, Any

class MonitoringAgent:
    """Simulates or reads events like traffic delays and fuel price changes."""
    def __init__(self, graph):
        self.graph = graph
        self.current_fuel_price = 1.5  # $ per liter baseline

    def simulate_traffic_delay(self):
        # pick a random edge and increase its time by a factor
        edges = list(self.graph.edges)
        edge = random.choice(edges)
        severity = random.uniform(1.2, 3.0)
        return {"type": "traffic", "edge": edge, "severity": severity}

    def simulate_fuel_change(self):
        change = random.uniform(-0.2, 0.5)
        self.current_fuel_price = max(0.5, self.current_fuel_price + change)
        return {"type": "fuel", "new_price": round(self.current_fuel_price, 3)}

    def inject_event(self, event: Dict[str, Any]):
        return event
