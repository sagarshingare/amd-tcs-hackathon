import random
from typing import Dict

class ExternalAPIAgent:
    """Mock external API agent for traffic and weather feed simulation."""
    def __init__(self):
        self.sources = ["MockTrafficAPI", "MockWeatherFeed"]

    def fetch_traffic_feed(self) -> Dict:
        return {
            "source": self.sources[0],
            "congestion_index": round(random.uniform(0.2, 0.9), 2),
            "alert": random.choice(["normal", "moderate", "heavy"]),
        }

    def fetch_weather_feed(self) -> Dict:
        condition = random.choice(["clear", "rain", "fog", "storm"])
        return {
            "source": self.sources[1],
            "condition": condition,
            "severity": random.choice(["low", "medium", "high"]),
        }

    def get_combined_feed(self) -> Dict:
        return {
            "traffic": self.fetch_traffic_feed(),
            "weather": self.fetch_weather_feed(),
        }
