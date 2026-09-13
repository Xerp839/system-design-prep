import uuid
from typing import List
from .parking_slot import ParkingSlot
from .vehicle import Vehicle

class Floor:
    """
    Floor Domain Model
    
    Represents a floor in the parking lot containing multiple slots.
    """
    def __init__(self, floor_number: int):
        self.id = str(uuid.uuid4())
        self.floor_number = floor_number
        self.slots: List[ParkingSlot] = []

    def add_slot(self, slot: ParkingSlot):
        self.slots.append(slot)

    def get_available_slots(self, vehicle_type: Vehicle.VehicleType) -> List[ParkingSlot]:
        return [s for s in self.slots if s.slot_type == vehicle_type and not s.occupied]

    def get_available_slots_count(self, vehicle_type: Vehicle.VehicleType) -> int:
        return len(self.get_available_slots(vehicle_type))

    def __str__(self):
        return f"Floor(id={self.id}, number={self.floor_number}, total_slots={len(self.slots)})"
