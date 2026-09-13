import threading
from typing import Dict, Optional

from domain.parking_slot import ParkingSlot
from domain.vehicle import VehicleType
from repository.floor_repository import FloorRepository


class SlotService:
    """
    Owns the allocation POLICY: which free slot we hand out.

    Today the policy is "lowest floor first, first free slot on it". Changing it to
    nearest-to-exit or cheapest-floor touches this method only.
    """

    def __init__(self, floor_repository: FloorRepository):
        self._floor_repository = floor_repository
        # Find-then-occupy is two steps; without this, two gates can win the same slot.
        # In a real DB this becomes UPDATE ... WHERE id=? AND occupied=false.
        self._lock = threading.Lock()

    def allocate_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        with self._lock:
            for floor in sorted(
                self._floor_repository.find_all(), key=lambda f: f.floor_number
            ):
                slot = floor.find_free_slot(vehicle_type)
                if slot:
                    slot.occupy()
                    return slot
            return None

    def release_slot(self, slot_id: str):
        with self._lock:
            slot = self._floor_repository.find_slot(slot_id)
            if slot:
                slot.release()

    def availability(self, vehicle_type: VehicleType) -> Dict[int, int]:
        """Free slots per floor - what an entrance display board would show."""
        return {
            f.floor_number: f.available_count(vehicle_type)
            for f in self._floor_repository.find_all()
        }
