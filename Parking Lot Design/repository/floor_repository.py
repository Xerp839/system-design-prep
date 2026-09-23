from typing import Dict, List, Optional

from domain.floor import Floor
from domain.parking_slot import ParkingSlot


class FloorRepository:
    """
    Stores floors. Slots live inside their floor - there is exactly one copy of
    each slot - but we keep an id -> slot index so releasing at exit is O(1)
    instead of a walk over every floor.
    """

    def __init__(self):
        self._floors: List[Floor] = []
        self._slots_by_id: Dict[str, ParkingSlot] = {}

    def save(self, floor: Floor) -> Floor:
        self._floors.append(floor)
        self.index_slots(floor)
        return floor

    def index_slots(self, floor: Floor):
        for slot in floor.slots:
            self._slots_by_id[slot.id] = slot

    def find_all(self) -> List[Floor]:
        return list(self._floors)

    def find_slot(self, slot_id: str) -> Optional[ParkingSlot]:
        return self._slots_by_id.get(slot_id)
