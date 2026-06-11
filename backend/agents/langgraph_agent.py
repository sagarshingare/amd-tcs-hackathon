"""LangGraphAgent

Optional integration with LangGraph for orchestrating agent communication
and producing a final, human-friendly decision explanation.

If the `langgraph` package is not available, this module falls back to
an internal aggregator that composes explanations deterministically.
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class LangGraphAgent:
    """A thin wrapper to orchestrate messages between agents using LangGraph.

    This keeps calls idempotent and provides a fallback when LangGraph isn't
    installed so the system remains operational in production without the
    external dependency.
    """

    def __init__(self, enable_langgraph: bool = False, llm_name: Optional[str] = None):
        self.enable_langgraph = enable_langgraph
        self.llm_name = llm_name or "local-fallback"
        self._client = None
        if enable_langgraph:
            try:
                import langgraph as lg  # type: ignore
                # initialize client (the real API may differ)
                self._client = lg.Client()
                logger.info("LangGraph client initialized")
            except Exception as e:
                logger.warning("LangGraph not available, falling back: %s", e)
                self.enable_langgraph = False

    def compose_explanation(self, context: Dict[str, Any]) -> str:
        """Compose a human-friendly explanation from the provided context.

        Context is expected to include: `source`, `target`, `best_plan`,
        `vehicle_plans`, `disruptions`, and `real_time_data` (optional).
        """
        if self.enable_langgraph and self._client:
            try:
                # For production: build a small LangGraph network that summarizes
                # agent outputs and returns a concise explanation. Here we call
                # into a client API; adapt this block to your LangGraph setup.
                response = self._client.summarize(context, model=self.llm_name)
                return response.get("text", str(response))
            except Exception as e:
                logger.exception("LangGraph summarization failed, falling back: %s", e)

        # Fallback deterministic composer
        return self._fallback_compose(context)

    def _fallback_compose(self, context: Dict[str, Any]) -> str:
        best = context.get("best_plan", {})
        vehicle = best.get("vehicle", {})
        route = best.get("route", {})
        cost = best.get("cost", {})
        disruptions = context.get("disruptions", {})
        realtime = context.get("real_time_data", {})

        parts: List[str] = []
        parts.append(
            f"Recommended vehicle: {vehicle.get('name', 'unknown')} ({vehicle.get('type','-')})."
        )
        if route:
            parts.append(
                f"Route nodes: {route.get('path', [])}. Estimated time: {route.get('time', 0):.2f} min, distance: {route.get('distance', 0):.2f} km."
            )
        if cost:
            parts.append(f"Estimated cost: ${cost.get('total_cost', 0):.2f}; CO2: {cost.get('carbon_kg', 0):.2f} kg.")
        if disruptions:
            parts.append(f"Active disruptions: {len(disruptions)} segments affected.")
        if realtime:
            t = realtime.get('traffic')
            w = realtime.get('weather')
            if t:
                parts.append(f"Live traffic data source: {t.get('source','live')}; avg congestion: {t.get('average_congestion', 'n/a')}")
            if w:
                parts.append(f"Weather: {w.get('condition','n/a')}; travel multiplier: {w.get('travel_time_multiplier',1.0)}")

        parts.append("Decision made by aggregating routing, cost and disruption agents; choose the plan with lowest total cost.")
        return " ".join(parts)
