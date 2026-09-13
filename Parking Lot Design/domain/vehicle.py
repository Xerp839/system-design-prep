from enum import Enum


class VehicleType(Enum):
    BIKE = "BIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"
    EV = "EV"


class Vehicle:
    """A vehicle entering the lot. The license plate is its natural identity."""

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

    def __str__(self):
        return f"{self.license_plate} ({self.vehicle_type.value})"
