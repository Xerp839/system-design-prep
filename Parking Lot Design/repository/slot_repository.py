from typing import List, Optional, Dict
from domain.parking_slot import ParkingSlot
from domain.vehicle import Vehicle

class SlotRepository:
    def __init__(self):
        self._slots: Dict[str, ParkingSlot] = {}

    def save(self, slot: ParkingSlot) -> ParkingSlot:
        self._slots[slot.id] = slot
        return slot

    def find_by_id(self, slot_id: str) -> Optional[ParkingSlot]:
        return self._slots.get(slot_id)

    def find_available_slots(self, vehicle_type: Vehicle.VehicleType) -> List[ParkingSlot]:
        return [s for s in self._slots.values() if s.slot_type == vehicle_type and not s.occupied]

    def allocate_slot(self, vehicle_type: Vehicle.VehicleType) -> Optional[ParkingSlot]:
        for slot in self._slots.values():
            if slot.slot_type == vehicle_type and not slot.occupied:
                slot.occupied = True
                return slot
        return None

    def release_slot(self, slot_id: str):
        slot = self._slots.get(slot_id)
        if slot:
            slot.occupied = False

    def get_slot_statistics(self) -> Dict[str, int]:
        stats = {}
        for slot in self._slots.values():
            stats[slot.slot_type.value] = stats.get(slot.slot_type.value, 0) + 1
        return stats

    def clear(self):
        self._slots.clear()
