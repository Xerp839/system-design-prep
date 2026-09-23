from enum import Enum

class VehicleType(Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    TRUCK = "TRUCK"
    EV = "EV"

class Vehicle:

    def __init__(self, licencePlate: str, vehicleType: VehicleType):

        self.licence_plate = licencePlate
        self.vehicle_type = vehicleType

    def __str__(self):
        return f"{self.licencePlate.value} ({self.vehicle_type.value})"