from typing import Dict

class CostAgent:
    """Calculates cost using distance, fuel price, and vehicle efficiency."""
    def __init__(self, fuel_price: float = 1.5, vehicle_efficiency_km_per_liter: float = 12.0):
        self.fuel_price = fuel_price
        self.default_efficiency = vehicle_efficiency_km_per_liter
        self.emissions_factor = 2.31  # kg CO2 per liter

    def update_fuel_price(self, price: float):
        self.fuel_price = price

    def estimate_cost(self, distance_km: float, efficiency_km_per_liter: float = None) -> Dict:
        efficiency = efficiency_km_per_liter or self.default_efficiency
        liters = distance_km / efficiency
        fuel_cost = liters * self.fuel_price
        overhead_cost = 0.12 * fuel_cost
        total_cost = fuel_cost + overhead_cost
        carbon_kg = self.carbon_estimate(liters)
        return {
            "distance_km": distance_km,
            "efficiency_km_per_liter": efficiency,
            "liters": liters,
            "fuel_cost": round(fuel_cost, 3),
            "overhead_cost": round(overhead_cost, 3),
            "total_cost": round(total_cost, 3),
            "carbon_kg": round(carbon_kg, 3),
        }

    def carbon_estimate(self, liters: float) -> float:
        return liters * self.emissions_factor
