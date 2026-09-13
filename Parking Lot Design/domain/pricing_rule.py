from .vehicle import VehicleType


class PricingRule:
    """What one vehicle type costs. Data, not code - so new prices need no new logic."""

    def __init__(self, vehicle_type: VehicleType, rate_per_hour: float, flat_rate: float):
        self.vehicle_type = vehicle_type
        self.rate_per_hour = rate_per_hour
        self.flat_rate = flat_rate

    def __str__(self):
        return (
            f"{self.vehicle_type.value}: {self.rate_per_hour}/hr, "
            f"flat {self.flat_rate}"
        )
