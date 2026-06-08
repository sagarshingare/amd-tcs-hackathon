import aiohttp
import asyncio
import random
from typing import Dict, List, Optional
import os


class RealTimeDataFetcher:
    """Fetches real-time traffic, weather, and fuel price data from APIs."""
    
    def __init__(self):
        # API Keys (use environment variables in production)
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "mock_key")
        self.fuel_api_key = os.getenv("FUEL_API_KEY", "mock_key")
        self.maps_api_key = os.getenv("MAPS_API_KEY", "mock_key")
        self.base_urls = {
            "weather": "https://api.openweathermap.org/data/2.5/weather",
            "fuel_us": "https://api.eia.gov/series/PET_EMD_EPD2D_PTE_NUS_DPG.json",
            "traffic": "https://api.tomtom.com/traffic/services/4/currentFlow",
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def fetch_traffic_data(self, coordinates: List[tuple]) -> Dict:
        """Fetch real-time traffic from API or return mock data."""
        try:
            # For demo: return mock data with realistic patterns
            return await self._mock_traffic_data(coordinates)
        except Exception as e:
            return {"error": str(e), "traffic": self._fallback_traffic()}

    async def fetch_weather_data(self, latitude: float, longitude: float) -> Dict:
        """Fetch real-time weather from OpenWeatherMap or mock."""
        try:
            # For demo: return mock data
            return await self._mock_weather_data(latitude, longitude)
        except Exception as e:
            return {"error": str(e), "weather": self._fallback_weather()}

    async def fetch_fuel_prices(self) -> Dict:
        """Fetch real-time fuel prices from EIA API or mock."""
        try:
            return await self._mock_fuel_data()
        except Exception as e:
            return {"error": str(e), "fuel": self._fallback_fuel()}

    async def _mock_traffic_data(self, coordinates: List[tuple]) -> Dict:
        """Mock traffic data with realistic variance."""
        segments = []
        for i, (lat, lon) in enumerate(coordinates):
            congestion = random.uniform(0.1, 0.95)
            speed_factor = 1.0 if congestion < 0.3 else (0.7 if congestion < 0.6 else 0.4)
            segments.append({
                "segment_id": i,
                "latitude": lat,
                "longitude": lon,
                "congestion_index": round(congestion, 2),
                "speed_factor": round(speed_factor, 2),
                "incident": random.choice([None, "accident", "construction"]) if congestion > 0.7 else None,
            })
        return {
            "source": "MockTrafficAPI",
            "timestamp": "2026-06-09T12:00:00Z",
            "segments": segments,
            "average_congestion": round(sum(s['congestion_index'] for s in segments) / len(segments), 2),
        }

    async def _mock_weather_data(self, latitude: float, longitude: float) -> Dict:
        """Mock weather data with realistic conditions."""
        conditions = ["clear", "clouds", "rain", "thunderstorm", "fog"]
        condition = random.choices(conditions, weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
        impact_factor = {"clear": 1.0, "clouds": 1.05, "rain": 1.2, "thunderstorm": 1.5, "fog": 1.3}
        return {
            "source": "MockWeatherAPI",
            "latitude": latitude,
            "longitude": longitude,
            "condition": condition,
            "temperature": round(random.uniform(50, 90), 1),
            "humidity": round(random.uniform(30, 90), 1),
            "wind_speed_kmh": round(random.uniform(0, 40), 1),
            "travel_time_multiplier": impact_factor[condition],
            "timestamp": "2026-06-09T12:00:00Z",
        }

    async def _mock_fuel_data(self) -> Dict:
        """Mock fuel price data with realistic variance."""
        base_price = 1.5
        variation = random.uniform(-0.2, 0.35)
        return {
            "source": "MockFuelPriceAPI",
            "diesel_price_usd_per_liter": round(base_price + variation, 3),
            "gasoline_price_usd_per_liter": round(base_price + variation - 0.05, 3),
            "trend": random.choice(["up", "down", "stable"]),
            "timestamp": "2026-06-09T12:00:00Z",
            "region": "US-National",
        }

    def _fallback_traffic(self) -> Dict:
        return {"status": "fallback", "congestion_index": 0.3}

    def _fallback_weather(self) -> Dict:
        return {"status": "fallback", "condition": "clear", "travel_time_multiplier": 1.0}

    def _fallback_fuel(self) -> Dict:
        return {"status": "fallback", "diesel_price_usd_per_liter": 1.5}

    async def fetch_all_data(self, coordinates: List[tuple], lat: float, lon: float) -> Dict:
        """Fetch all real-time data concurrently."""
        traffic, weather, fuel = await asyncio.gather(
            self.fetch_traffic_data(coordinates),
            self.fetch_weather_data(lat, lon),
            self.fetch_fuel_prices(),
        )
        return {
            "traffic": traffic,
            "weather": weather,
            "fuel": fuel,
        }
