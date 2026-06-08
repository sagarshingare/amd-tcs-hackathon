from typing import Dict, Any

class DecisionAgent:
    """Orchestration controller which calls routing, cost agents and explains decisions."""
    def __init__(self, routing_agent, cost_agent, disruption_agent, monitoring_agent, graph):
        self.routing = routing_agent
        self.cost = cost_agent
        self.disruption = disruption_agent
        self.monitor = monitoring_agent
        self.graph = graph
        self.current_plan = None
        self.previous_plan = None

    def optimize_route(self, source: int, target: int) -> Dict[str, Any]:
        plan = self.routing.shortest_path_by_time(source, target)
        if 'error' in plan:
            return {"error": plan['error']}
        cost_info = self.cost.estimate_cost(plan['distance'])
        explanation = self.explain_decision(source, target, plan, cost_info)
        self.previous_plan = self.current_plan
        self.current_plan = {"route": plan, "cost": cost_info, "explanation": explanation}
        return self.current_plan

    def handle_disruption(self, event: Dict[str, Any], source: int, target: int) -> Dict[str, Any]:
        # apply disruption
        if event['type'] == 'traffic':
            self.disruption.apply_traffic_disruption(event['edge'], event['severity'])
        elif event['type'] == 'fuel':
            self.cost.update_fuel_price(event['new_price'])
            self.disruption.apply_fuel_change(event['new_price'])

        # re-optimize
        updated = self.optimize_route(source, target)
        return {"event": event, "updated_plan": updated}

    def explain_decision(self, source, target, plan: Dict, cost_info: Dict) -> str:
        # Provide human-readable explanation
        path = plan.get('path')
        time = plan.get('time')
        dist = plan.get('distance')
        explanation = (
            f"Selected route from {source} to {target} via nodes {path}. "
            f"Estimated travel time {time:.2f} minutes and distance {dist:.2f} km. "
            f"Estimated cost ${cost_info['total_cost']:.2f} (fuel ${cost_info['fuel_cost']:.2f})."
        )
        # mention disruptions if present
        if getattr(self.disruption, 'disrupted_edges', None):
            explanation += f" Disruptions detected on edges: {list(self.disruption.disrupted_edges.keys())}."
        return explanation
