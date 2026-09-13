import uuid
from .vehicle import Vehicle

class PricingRule:
    """
    PricingRule Domain Model
    
    Defines the pricing for a specific vehicle type.
    """
    def __init__(self, vehicle_type: Vehicle.VehicleType, rate_per_hour: float, flat_rate: float):
        self.id = str(uuid.uuid4())
        self.vehicle_type = vehicle_type
        self.rate_per_hour = rate_per_hour
        self.flat_rate = flat_rate

    def update_rates(self, rate_per_hour: float, flat_rate: float):
        self.rate_per_hour = rate_per_hour
        self.flat_rate = flat_rate

    def __str__(self):
        return f"PricingRule(type={self.vehicle_type.value}, rate={self.rate_per_hour}, flat={self.flat_rate})"
