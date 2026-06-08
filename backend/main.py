from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

from backend.data.sample_data import sample_graph
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.routing_agent import RoutingAgent
from backend.agents.cost_agent import CostAgent
from backend.agents.disruption_agent import DisruptionAgent
from backend.agents.decision_agent import DecisionAgent

app = FastAPI(title="Agentic AI Logistics Optimization System")

# Initialize graph and agents
G = sample_graph()
monitor = MonitoringAgent(G)
disruption = DisruptionAgent(G)
routing = RoutingAgent(G)
cost_agent = CostAgent(fuel_price=monitor.current_fuel_price)
decision = DecisionAgent(routing, cost_agent, disruption, monitor, G)


class OptimizeRequest(BaseModel):
    source: Optional[int] = 0
    target: Optional[int] = 1


class DisruptRequest(BaseModel):
    type: str
    edge: Optional[list] = None
    severity: Optional[float] = None
    new_price: Optional[float] = None


@app.get("/graph")
def get_graph():
    nodes = [{"id": n, "pos": G.nodes[n].get('pos', (0, 0))} for n in G.nodes]
    edges = [{"u": u, "v": v, "dist": G[u][v]['distance'], 'time': G[u][v]['time']} for u, v in G.edges]
    return {"nodes": nodes, "edges": edges}


@app.post("/optimize")
def optimize(req: OptimizeRequest):
    plan = decision.optimize_route(req.source, req.target)
    return plan


@app.post("/disrupt")
def disrupt(req: DisruptRequest):
    event = None
    if req.type == 'traffic':
        if req.edge is None or req.severity is None:
            return {"error": "edge and severity required for traffic"}
        event = {"type": "traffic", "edge": tuple(req.edge), "severity": req.severity}
    elif req.type == 'fuel':
        if req.new_price is None:
            return {"error": "new_price required for fuel"}
        event = {"type": "fuel", "new_price": req.new_price}
    else:
        return {"error": "unknown event type"}

    result = decision.handle_disruption(event, source=0, target=1)
    return result


@app.get("/status")
def status():
    return {"current_plan": decision.current_plan, "disruptions": disruption.disrupted_edges}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
