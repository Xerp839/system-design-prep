from typing import List, Optional

from .parking_slot import ParkingSlot
from .vehicle import VehicleType


class Floor:
    """A floor owns its slots. This is the single source of truth for slot state."""

    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.slots: List[ParkingSlot] = []

    def add_slots(self, slot_type: VehicleType, count: int) -> List[ParkingSlot]:
        created = []
        for _ in range(count):
            slot_id = f"S-F{self.floor_number}-{len(self.slots) + 1:03d}"
            slot = ParkingSlot(slot_id, slot_type, self.floor_number)
            self.slots.append(slot)
            created.append(slot)
        return created

    def find_free_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        return next(
            (s for s in self.slots if s.slot_type == vehicle_type and not s.occupied),
            None,
        )

    def available_count(self, vehicle_type: VehicleType) -> int:
        return sum(
            1 for s in self.slots if s.slot_type == vehicle_type and not s.occupied
        )

    def __str__(self):
        return f"Floor {self.floor_number} ({len(self.slots)} slots)"
