import random
from typing import Dict, Any

class MonitoringAgent:
    """Simulates or reads events like traffic delays, fuel price changes, and weather disruptions."""
    def __init__(self, graph):
        self.graph = graph
        self.current_fuel_price = 1.5  # $ per liter baseline
        self.current_weather = "clear"

    def simulate_traffic_delay(self) -> Dict[str, Any]:
        edges = list(self.graph.edges)
        edge = random.choice(edges)
        severity = random.uniform(1.3, 2.8)
        return {
            "type": "traffic",
            "edge": edge,
            "severity": round(severity, 2),
            "description": "Heavy congestion on a primary segment",
        }

    def simulate_fuel_change(self) -> Dict[str, Any]:
        change = random.uniform(-0.15, 0.45)
        self.current_fuel_price = max(0.6, self.current_fuel_price + change)
        return {
            "type": "fuel",
            "new_price": round(self.current_fuel_price, 3),
            "description": "Dynamic fuel market changed regional diesel prices",
        }

    def simulate_weather_disruption(self) -> Dict[str, Any]:
        edge = random.choice(list(self.graph.edges))
        severity = random.uniform(1.2, 2.4)
        self.current_weather = random.choice(["rain", "storm", "fog"])
        return {
            "type": "weather",
            "edge": edge,
            "severity": round(severity, 2),
            "weather": self.current_weather,
            "description": f"{self.current_weather.title()} causing slower movement on a route segment",
        }

    def simulate_event(self) -> Dict[str, Any]:
        choice = random.choice(["traffic", "fuel", "weather"])
        if choice == "traffic":
            return self.simulate_traffic_delay()
        if choice == "fuel":
            return self.simulate_fuel_change()
        return self.simulate_weather_disruption()

    def inject_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return event
