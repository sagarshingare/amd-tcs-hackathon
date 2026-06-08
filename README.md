# Agentic AI Logistics Optimization System

Problem:

Create an autonomous multi-agent system that optimizes transportation routes, cost, and delivery efficiency in real-time, adapts to disruptions (traffic, fuel price changes), and explains decisions.

Solution Overview:

- Backend: FastAPI with modular agents (Monitoring, Routing, Cost, Disruption, Decision) plus mocked external feed support.
- Frontend: Streamlit dashboard to run optimization, inject disruptions, compare initial and updated routes, and view explanations.
- Optimization: NetworkX grid graph planner with vehicle-aware cost, emissions scoring, and weather/traffic disruption handling.

Architecture (text diagram):

Client (Streamlit) <-> FastAPI endpoints
                      ├─ DecisionAgent (orchestrates)
                      ├─ RoutingAgent (NetworkX optimizer)
                      ├─ CostAgent (cost model)
                      ├─ MonitoringAgent (simulates events)
                      └─ DisruptionAgent (detects anomalies)

Setup

1. Create virtualenv and install:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run backend:

```bash
./scripts/run_backend.sh
```

3. In another terminal run frontend:

```bash
./scripts/run_frontend.sh
```

Alternatively:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
streamlit run frontend/app.py
```

Demo flow

- Click `Run Optimization` to compute an initial route and fleet-aware route plan.
- Click `Generate a random disruption` to simulate a traffic, weather, or fuel event.
- Use `Inject custom disruption` to test traffic delays, weather slowdowns, or fuel price shocks.
- View initial/updated routes, cost comparison, disruption details, and AI explanations.

Bonus features

- Multi-vehicle fleet planning with van, truck, and hybrid options.
- Carbon emission scoring for route decisions.
- Mock external real-time feed endpoints for traffic and weather data.
- Reinforcement learning placeholder agent included for future policy upgrades.

Future improvements

- Integrate OR-Tools for vehicle routing problems (VRP) with multiple stops and vehicles.
- Hook to live APIs for traffic, weather, and fuel prices.
- Add RL-based agent for learning policies across repeated runs.
- Improve explanation with an LLM backend (LangChain integration) for richer narratives.

Files

- `backend/` - FastAPI app + agents
- `frontend/` - Streamlit UI
- `requirements.txt` - dependencies
