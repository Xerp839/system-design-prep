from typing import List, Optional, Dict
from domain.floor import Floor

class FloorRepository:
    def __init__(self):
        self._floors: Dict[str, Floor] = {}
        self._floor_number_to_id: Dict[int, str] = {}

    def save(self, floor: Floor) -> Floor:
        self._floors[floor.id] = floor
        self._floor_number_to_id[floor.floor_number] = floor.id
        return floor

    def find_by_id(self, floor_id: str) -> Optional[Floor]:
        return self._floors.get(floor_id)

    def find_by_number(self, floor_number: int) -> Optional[Floor]:
        floor_id = self._floor_number_to_id.get(floor_number)
        return self._floors.get(floor_id) if floor_id else None

    def find_all(self) -> List[Floor]:
        return list(self._floors.values())

    def exists_by_number(self, floor_number: int) -> bool:
        return floor_number in self._floor_number_to_id

    def delete(self, floor_id: str):
        floor = self._floors.pop(floor_id, None)
        if floor:
            self._floor_number_to_id.pop(floor.floor_number, None)

    def clear(self):
        self._floors.clear()
        self._floor_number_to_id.clear()
