from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import random

from backend.data.sample_data import sample_graph
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.routing_agent import RoutingAgent
from backend.agents.cost_agent import CostAgent
from backend.agents.disruption_agent import DisruptionAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.external_api_agent import RealTimeDataFetcher

app = FastAPI(title="Agentic AI Logistics Optimization System")

# Initialize graph and agents
G = sample_graph()
monitor = MonitoringAgent(G)
disruption = DisruptionAgent(G)
real_time_fetcher = RealTimeDataFetcher()
routing = RoutingAgent(G)
cost_agent = CostAgent(fuel_price=monitor.current_fuel_price)
fleet = [
    {"id": 1, "name": "Delivery Van", "type": "van", "efficiency_km_per_liter": 10.0, "capacity": 1200},
    {"id": 2, "name": "Electric Truck", "type": "truck", "efficiency_km_per_liter": 6.5, "capacity": 2500},
    {"id": 3, "name": "Hybrid Fleet Car", "type": "hybrid", "efficiency_km_per_liter": 15.0, "capacity": 800},
]
decision = DecisionAgent(routing, cost_agent, disruption, monitor, G, fleet)


class OptimizeRequest(BaseModel):
    source: Optional[int] = 0
    target: Optional[int] = 19
    use_real_time_data: Optional[bool] = False


class DisruptRequest(BaseModel):
    type: str
    edge: Optional[List[int]] = None
    severity: Optional[float] = None
    new_price: Optional[float] = None


@app.get("/graph")
def get_graph():
    nodes = [
        {"id": n, "pos": G.nodes[n].get('pos', (0, 0)), "name": G.nodes[n].get('name', f"Node {n}")}
        for n in G.nodes
    ]
    edges = [
        {
            "u": u,
            "v": v,
            "dist": G[u][v]['distance'],
            "time": G[u][v]['time'],
            "road_quality": G[u][v].get('road_quality', 'unknown'),
        }
        for u, v in G.edges
    ]
    return {"nodes": nodes, "edges": edges, "fleet": fleet, "fuel_price": monitor.current_fuel_price}


@app.post("/optimize")
async def optimize(req: OptimizeRequest):
    if req.use_real_time_data:
        coordinates = [G.nodes[n]['pos'] for n in G.nodes()]
        lat, lon = coordinates[0] if coordinates else (0, 0)
        real_time_data = await real_time_fetcher.fetch_all_data(coordinates, lat, lon)
        
        if real_time_data.get('weather', {}).get('travel_time_multiplier', 1.0) > 1.1:
            edges = list(G.edges)
            for edge in random.sample(edges, min(2, len(edges))):
                multiplier = real_time_data['weather']['travel_time_multiplier']
                disruption.apply_weather_disruption(edge, multiplier - 1.0, real_time_data['weather']['condition'])
        
        if 'fuel' in real_time_data:
            new_price = real_time_data['fuel'].get('diesel_price_usd_per_liter', monitor.current_fuel_price)
            monitor.current_fuel_price = new_price
            cost_agent.update_fuel_price(new_price)
        
        plan = decision.optimize_route(req.source, req.target)
        plan['real_time_data'] = real_time_data
        return plan
    else:
        plan = decision.optimize_route(req.source, req.target)
        return plan


@app.post("/optimize_with_realtime")
async def optimize_with_realtime(req: OptimizeRequest):
    coordinates = [G.nodes[n]['pos'] for n in G.nodes()]
    lat, lon = coordinates[0] if coordinates else (0, 0)
    real_time_data = await real_time_fetcher.fetch_all_data(coordinates, lat, lon)
    
    if real_time_data.get('traffic', {}).get('segments'):
        for segment in real_time_data['traffic']['segments'][:3]:
            if segment['congestion_index'] > 0.6:
                edges = list(G.edges)
                for edge in random.sample(edges, min(1, len(edges))):
                    severity = 1.0 + segment['congestion_index']
                    disruption.apply_traffic_disruption(edge, severity)
    
    if real_time_data.get('weather', {}).get('travel_time_multiplier', 1.0) > 1.05:
        weather = real_time_data['weather']
        edges = list(G.edges)
        for edge in random.sample(edges, min(2, len(edges))):
            disruption.apply_weather_disruption(edge, weather['travel_time_multiplier'] - 1.0, weather['condition'])
    
    if 'fuel' in real_time_data:
        new_price = real_time_data['fuel'].get('diesel_price_usd_per_liter', monitor.current_fuel_price)
        monitor.current_fuel_price = new_price
        cost_agent.update_fuel_price(new_price)
    
    plan = decision.optimize_route(req.source, req.target)
    plan['real_time_data'] = real_time_data
    return plan


@app.post("/disrupt")
def disrupt(req: DisruptRequest):
    if req.type == 'traffic':
        if req.edge is None or req.severity is None:
            return {"error": "edge and severity required for traffic"}
        event = {"type": "traffic", "edge": tuple(req.edge), "severity": req.severity}
    elif req.type == 'weather':
        if req.edge is None or req.severity is None:
            return {"error": "edge and severity required for weather"}
        event = {"type": "weather", "edge": tuple(req.edge), "severity": req.severity, "weather": "storm"}
    elif req.type == 'fuel':
        if req.new_price is None:
            return {"error": "new_price required for fuel"}
        event = {"type": "fuel", "new_price": req.new_price}
    else:
        return {"error": "unknown event type"}

    result = decision.handle_disruption(event, source=0, target=19)
    return result


@app.post("/simulate_event")
async def simulate_event():
    event = monitor.simulate_event()
    result = decision.handle_disruption(event, source=0, target=19)
    return {"event": event, "updated_plan": result}


@app.post("/reset")
def reset_system():
    disruption.clear_disruptions()
    monitor.current_fuel_price = 1.5
    decision.previous_plan = None
    decision.current_plan = None
    return {"status": "reset", "fuel_price": monitor.current_fuel_price, "disruptions": disruption.disrupted_edges}


@app.get("/feeds")
async def feeds():
    coordinates = [G.nodes[n]['pos'] for n in G.nodes()]
    lat, lon = coordinates[0] if coordinates else (0, 0)
    return await real_time_fetcher.fetch_all_data(coordinates, lat, lon)


@app.get("/status")
def status():
    return {
        "current_plan": decision.current_plan,
        "disruptions": disruption.disrupted_edges,
        "fuel_price": monitor.current_fuel_price,
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
