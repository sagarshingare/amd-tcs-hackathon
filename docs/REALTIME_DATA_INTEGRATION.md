# Real-Time Data Integration Guide for Logistics System

## Overview

The system integrates real-time datasets from external APIs for traffic, weather, and fuel prices. This guide covers data sources, integration patterns, and dynamic passing through the agent pipeline.

---

## 1. DATA SOURCES

### Traffic Data
- **Google Maps Distance Matrix API**: `https://maps.googleapis.com/maps/api/distancematrix/json`
  - Requires: API key, origins, destinations
  - Returns: Travel time, distance matrices
  - Cost: ~$0.005 per request (500K free/month)

- **TomTom Traffic API**: `https://api.tomtom.com/traffic/services/4/currentFlow`
  - Provides: Real-time traffic flow, congestion
  - Returns: Speed factor (0-1), incidents
  - Cost: ~$0.50/1000 requests

- **HERE Maps Routing API**: `https://api.here.com/routing/v8/routes`
  - Real-time route with traffic
  - Returns: Alternative routes with traffic delay

### Weather Data
- **OpenWeatherMap**: `https://api.openweathermap.org/data/2.5/weather`
  - Requires: lat, lon, API key
  - Returns: condition, wind, humidity
  - Cost: Free tier (60 calls/min)

- **WeatherAPI**: `https://api.weatherapi.com/v1/current.json`
  - Alternative to OpenWeatherMap
  - Similar pricing

### Fuel Prices
- **EIA (US Energy Agency)**: `https://api.eia.gov/series/PET_EMD_EPD2D_PTE_NUS_DPG.json`
  - US diesel/gas prices
  - Free, daily updates

- **Global Petrol Prices**: Web scraping or RSS feed
  - International prices
  - Requires web scraping

---

## 2. INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│ Streamlit UI (Frontend)                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Backend                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ RealTimeDataFetcher (external_api_agent.py)            │ │
│  │  • fetch_traffic_data()                                │ │
│  │  • fetch_weather_data()                                │ │
│  │  • fetch_fuel_prices()                                 │ │
│  │  • fetch_all_data() [async, concurrent]                │ │
│  └────────────────────────────────────────────────────────┘ │
│                        │                                      │
│                        ▼                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Decision Agent (orchestration)                         │ │
│  │  • Apply real-time disruptions                         │ │
│  │  • Update cost model with fuel prices                  │ │
│  │  • Re-optimize route                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                        │                                      │
│        ┌───────────────┼───────────────┐                     │
│        ▼               ▼               ▼                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ Disruption   │ │ Routing      │ │ Cost Agent   │         │
│  │ Agent        │ │ Agent        │ │              │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │ Graph (NetworkX)     │
        │ (edges have live     │
        │ travel times)        │
        └──────────────────────┘
```

---

## 3. HOW TO USE REAL-TIME DATA

### Option A: Direct API Integration (with real API keys)

```python
# 1. Set environment variables
export WEATHER_API_KEY="your_openweathermap_key"
export FUEL_API_KEY="your_eia_key"
export MAPS_API_KEY="your_tomtom_key"

# 2. Update RealTimeDataFetcher to use real endpoints
# In backend/agents/external_api_agent.py:
async def fetch_traffic_data_real(self, coordinates: List[tuple]) -> Dict:
    url = "https://api.tomtom.com/traffic/services/4/currentFlow"
    params = {
        "key": self.maps_api_key,
        "model": "absolute",
        "zoom": 10,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
```

### Option B: Using Mock Data (Current Implementation)

The system includes mock data that simulates realistic patterns:

```python
# Uses mock data internally
from backend.agents.external_api_agent import RealTimeDataFetcher

fetcher = RealTimeDataFetcher()
data = await fetcher.fetch_all_data(coordinates, lat, lon)

# Output format:
{
    "traffic": {
        "segments": [{
            "congestion_index": 0.72,
            "speed_factor": 0.4,
            "incident": "accident"
        }]
    },
    "weather": {
        "condition": "rain",
        "travel_time_multiplier": 1.2
    },
    "fuel": {
        "diesel_price_usd_per_liter": 1.68
    }
}
```

### Option C: Hybrid (Mock + Real APIs)

```python
# Use real APIs but fall back to mock on failure
class HybridFetcher(RealTimeDataFetcher):
    async def fetch_traffic_data(self, coordinates):
        try:
            return await self._fetch_from_real_api(coordinates)
        except Exception:
            return await self._mock_traffic_data(coordinates)
```

---

## 4. DYNAMIC DATA PASSING THROUGH AGENTS

### Flow 1: Static Simulation (Current)
```
POST /simulate_event
  ↓
MonitoringAgent creates random event
  ↓
DisruptionAgent applies to graph
  ↓
DecisionAgent re-optimizes
  ↓
Return updated route
```

### Flow 2: Real-Time Data (New)
```
POST /optimize_with_realtime
  ↓
RealTimeDataFetcher.fetch_all_data()
  ↓
Disruption Agent applies:
  - Traffic multipliers to edges
  - Weather slowdowns to edges
  ↓
Cost Agent updates fuel prices
  ↓
Decision Agent re-optimizes with real context
  ↓
Return route + real_time_data JSON
```

---

## 5. API ENDPOINTS FOR REAL-TIME DATA

### Fetch Live Data
```bash
GET /feeds
Response:
{
  "traffic": {...},
  "weather": {...},
  "fuel": {...}
}
```

### Optimize with Real-Time Data
```bash
POST /optimize_with_realtime
Body: {"source": 0, "target": 19}
Response:
{
  "best_plan": {...},
  "real_time_data": {
    "traffic": {...},
    "weather": {...},
    "fuel": {...}
  }
}
```

### Manual Disruption with Real-Time Context
```bash
POST /disrupt
Body: {
  "type": "traffic",
  "edge": [0, 1],
  "severity": 2.5
}
```

---

## 6. IMPLEMENTATION CHECKLIST

- [x] Mock data fetcher (RealTimeDataFetcher)
- [x] Async concurrent fetching (asyncio.gather)
- [x] Dynamic disruption application
- [x] Real-time fuel price updates
- [x] API endpoints for feeds
- [ ] Real API integrations (requires keys)
- [ ] Caching strategy (Redis recommended)
- [ ] Error handling + fallback logic
- [ ] Rate limiting + retry logic
- [ ] Data validation schema

---

## 7. SETUP FOR REAL API KEYS

### Get Traffic API Key (TomTom)
1. Register at: https://developer.tomtom.com/
2. Create API key
3. Set environment: `export MAPS_API_KEY="your_key"`

### Get Weather API Key (OpenWeatherMap)
1. Register at: https://openweathermap.org/api
2. Get free tier key
3. Set environment: `export WEATHER_API_KEY="your_key"`

### Get Fuel Prices (EIA)
1. Register at: https://www.eia.gov/opendata/
2. Get free tier key
3. No setup needed (free endpoint)

### Update Fetcher
Replace mock methods with real API calls:
```python
async def fetch_traffic_data(self, coordinates):
    async with aiohttp.ClientSession() as session:
        # Real API call here
        return data
```

---

## 8. BEST PRACTICES

1. **Cache Data**: Store fetched data for 5 minutes to reduce API calls
2. **Async/Await**: Always use async for parallel API calls
3. **Error Handling**: Fallback to mock if API fails
4. **Rate Limiting**: Implement backoff for rate-limited APIs
5. **Data Validation**: Validate all incoming data before applying
6. **Logging**: Log all API calls and disruptions for debugging
7. **Testing**: Use mock data for tests, real APIs in production

---

## 9. EXAMPLE: FULL FLOW

```bash
# Terminal 1: Start backend
python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Test real-time optimization
curl -X POST http://127.0.0.1:8000/optimize_with_realtime \
  -H "Content-Type: application/json" \
  -d '{"source": 0, "target": 19}'

# Response includes:
# {
#   "best_plan": {...route with vehicle...},
#   "real_time_data": {
#     "traffic": {...congestion data...},
#     "weather": {...weather impact...},
#     "fuel": {...price updates...}
#   }
# }
```

---

## 10. TROUBLESHOOTING

**Issue**: Mock data not applying disruptions
- Check: Edges exist in graph
- Check: Severity > 1.0

**Issue**: API key errors
- Check: Environment variables set
- Check: API key is valid and not expired

**Issue**: Slow optimization
- Check: Network latency to API
- Check: Use caching for repeated calls

**Issue**: Real-time data not in response
- Check: use_real_time_data flag is True
- Check: /feeds endpoint working

---

## Next Steps

1. Integrate real API keys from your logistics provider
2. Set up data caching (Redis) for production
3. Add monitoring/alerting for data freshness
4. Build dashboard showing live data quality
5. Implement feedback loop: actual vs predicted travel times
