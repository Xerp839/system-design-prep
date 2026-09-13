from typing import Optional
from domain.parking_slot import ParkingSlot
from domain.vehicle import Vehicle
from repository.slot_repository import SlotRepository

class SlotService:
    def __init__(self, slot_repository: SlotRepository):
        self._slot_repository = slot_repository

    def allocate_slot(self, vehicle_type: Vehicle.VehicleType) -> Optional[ParkingSlot]:
        return self._slot_repository.allocate_slot(vehicle_type)

    def release_slot(self, slot_id: str):
        self._slot_repository.release_slot(slot_id)

    def create_slot(self, slot_type: Vehicle.VehicleType, floor_number: int) -> ParkingSlot:
        slot = ParkingSlot(slot_type, floor_number)
        return self._slot_repository.save(slot)

    def get_available_slot_count(self, vehicle_type: Vehicle.VehicleType) -> int:
        return len(self._slot_repository.find_available_slots(vehicle_type))
