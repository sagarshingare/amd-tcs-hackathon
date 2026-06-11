from typing import Dict, Any, List, Optional
from backend.agents.langgraph_agent import LangGraphAgent


class DecisionAgent:
    """Orchestration controller which calls routing, cost agents and explains decisions.

    This agent now supports optional LangGraph-based explanation composition. If
    LangGraph is enabled (configured via `LangGraphAgent`), final decision
    explanations are composed by the LangGraph network; otherwise a deterministic
    textual explanation is returned.
    """

    def __init__(self, routing_agent, cost_agent, disruption_agent, monitoring_agent, graph, fleet: List[Dict[str, Any]], langgraph_agent: Optional[LangGraphAgent] = None):
        self.routing = routing_agent
        self.cost = cost_agent
        self.disruption = disruption_agent
        self.monitor = monitoring_agent
        self.graph = graph
        self.fleet = fleet
        self.langgraph = langgraph_agent or LangGraphAgent(enable_langgraph=False)
        self.current_plan = None
        self.previous_plan = None

    def optimize_route(self, source: int, target: int) -> Dict[str, Any]:
        vehicle_plans = []
        for vehicle in self.fleet:
            route = self.routing.shortest_path_by_time(source, target)
            if 'error' in route:
                vehicle_plans.append({"vehicle": vehicle, "error": route['error']})
                continue
            cost_info = self.cost.estimate_cost(route['distance'], vehicle['efficiency_km_per_liter'])
            vehicle_plans.append({"vehicle": vehicle, "route": route, "cost": cost_info})

        best = min(
            [plan for plan in vehicle_plans if 'cost' in plan],
            key=lambda plan: plan['cost']['total_cost'],
            default=None,
        )
        if not best:
            return {"error": "No feasible route found for any vehicle."}

        # Build context for explanation (used by LangGraph or fallback)
        context = {
            "source": source,
            "target": target,
            "best_plan": best,
            "vehicle_plans": vehicle_plans,
            "disruptions": getattr(self.disruption, 'disrupted_edges', {}),
        }
        explanation = self.langgraph.compose_explanation({**context, **{"real_time_data": None}})
        self.previous_plan = self.current_plan
        self.current_plan = {
            "best_plan": best,
            "vehicle_plans": vehicle_plans,
            "explanation": explanation,
        }
        return self.current_plan

    def handle_disruption(self, event: Dict[str, Any], source: int, target: int) -> Dict[str, Any]:
        if event['type'] == 'traffic':
            self.disruption.apply_traffic_disruption(event['edge'], event['severity'])
        elif event['type'] == 'weather':
            self.disruption.apply_weather_disruption(event['edge'], event['severity'], event.get('weather', 'unknown'))
        elif event['type'] == 'fuel':
            self.cost.update_fuel_price(event['new_price'])
            self.disruption.apply_fuel_change(event['new_price'])

        updated = self.optimize_route(source, target)
        return {"event": event, "updated_plan": updated}

    def compare_routes(self, previous: Dict[str, Any], current: Dict[str, Any]) -> str:
        if not previous or 'best_plan' not in previous or 'best_plan' not in current:
            return "This is the first optimization cycle."

        prev_cost = previous['best_plan']['cost']['total_cost']
        curr_cost = current['best_plan']['cost']['total_cost']
        diff = curr_cost - prev_cost
        if diff > 0:
            return f"Cost rose by ${diff:.2f} due to disruption and re-routing."
        if diff < 0:
            return f"Cost improved by ${abs(diff):.2f} after choosing a more efficient route or vehicle."
        return "The cost remained stable despite the disruption."

    def explain_decision(self, source, target, best_plan: Dict[str, Any], vehicle_plans: List[Dict[str, Any]]) -> str:
        # Backwards-compatible local explanation helper retained for callers
        # that prefer a direct string (LangGraph is used elsewhere).
        route = best_plan.get('route', {})
        cost_info = best_plan.get('cost', {})
        vehicle = best_plan.get('vehicle', {})
        explanation = (
            f"Best route for vehicle {vehicle.get('name','unknown')} ({vehicle.get('type','unknown')}) uses nodes {route.get('path',[])} with "
            f"estimated travel time {route.get('time',0):.2f} min and distance {route.get('distance',0):.2f} km. "
            f"Total cost is ${cost_info.get('total_cost',0):.2f} and estimated emissions are {cost_info.get('carbon_kg',0):.2f} kg CO2. "
        )
        if getattr(self.disruption, 'disrupted_edges', {}):
            explanation += (
                f"Re-optimization was triggered because of disruptions on {len(self.disruption.disrupted_edges)} segment(s). "
                f"Affected edges: {list(self.disruption.disrupted_edges.keys())}. "
            )
        explanation += self.compare_routes(self.previous_plan, self.current_plan)
        return explanation
