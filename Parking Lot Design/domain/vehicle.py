import uuid
from enum import Enum

class Vehicle:
    """
    Vehicle Domain Model
    
    Represents a vehicle entering/exiting the parking lot.
    """
    class VehicleType(Enum):
        BIKE = "BIKE"
        CAR = "CAR"
        TRUCK = "TRUCK"
        EV = "EV"

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.id = str(uuid.uuid4())
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

    def __str__(self):
        return f"Vehicle(id={self.id}, license_plate='{self.license_plate}', type={self.vehicle_type.value})"
