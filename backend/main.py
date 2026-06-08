from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from backend.data.sample_data import sample_graph
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.routing_agent import RoutingAgent
from backend.agents.cost_agent import CostAgent
from backend.agents.disruption_agent import DisruptionAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.external_api_agent import ExternalAPIAgent

app = FastAPI(title="Agentic AI Logistics Optimization System")

# Initialize graph and agents
G = sample_graph()
monitor = MonitoringAgent(G)
disruption = DisruptionAgent(G)
api_agent = ExternalAPIAgent()
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
def optimize(req: OptimizeRequest):
    plan = decision.optimize_route(req.source, req.target)
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
def simulate_event():
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
def feeds():
    return api_agent.get_combined_feed()


@app.get("/status")
def status():
    return {
        "current_plan": decision.current_plan,
        "disruptions": disruption.disrupted_edges,
        "fuel_price": monitor.current_fuel_price,
        "feeds": api_agent.get_combined_feed(),
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
