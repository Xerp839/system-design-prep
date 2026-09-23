from .vehicle import VehicleType

class PricingRule:

    def __init__(self, vehicletype : VehicleType, rateperhour: float, flat_rate : float):
        self.vehicle_type = vehicletype
        self.rate_per_hour = rateperhour
        self.flat_rate = flat_rate

    def __str__(self):
        return (
            f"{self.vehicle_type.value}: {self.rate_per_hour}/hr, "
            f"flat {self.flat_rate}"
        )