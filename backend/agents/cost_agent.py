from typing import Dict

class CostAgent:
    """Calculates cost using distance, fuel price, and vehicle efficiency."""
    def __init__(self, fuel_price: float = 1.5, vehicle_efficiency_km_per_liter: float = 12.0):
        self.fuel_price = fuel_price
        self.vehicle_efficiency = vehicle_efficiency_km_per_liter

    def update_fuel_price(self, price: float):
        self.fuel_price = price

    def estimate_cost(self, distance_km: float) -> Dict:
        liters = distance_km / self.vehicle_efficiency
        fuel_cost = liters * self.fuel_price
        other_cost = 0.1 * fuel_cost  # assumed overheads
        total = fuel_cost + other_cost
        return {"distance_km": distance_km, "liters": liters, "fuel_cost": fuel_cost, "other_cost": other_cost, "total_cost": total}

    def carbon_estimate(self, liters: float) -> float:
        # rough conversion: liters * 2.31 kg CO2 per liter (gasoline)
        return liters * 2.31
