import uuid
from .vehicle import Vehicle

class ParkingSlot:
    """
    ParkingSlot Domain Model
    
    Represents a single parking slot on a specific floor.
    """
    def __init__(self, slot_type: Vehicle.VehicleType, floor_number: int):
        self.id = str(uuid.uuid4())
        self.slot_type = slot_type
        self.occupied = False
        self.floor_number = floor_number

    def __str__(self):
        return f"ParkingSlot(id={self.id}, type={self.slot_type.value}, occupied={self.occupied}, floor={self.floor_number})"
