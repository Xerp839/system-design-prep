from .vehicle import VehicleType


class ParkingSlot:
    """One slot on one floor. `occupied` is the only state that changes."""

    def __init__(self, slot_id: str, slot_type: VehicleType, floor_number: int):
        self.id = slot_id
        self.slot_type = slot_type
        self.floor_number = floor_number
        self.occupied = False

    def occupy(self):
        # Guarded so a double-book is a loud error instead of a silent overwrite.
        if self.occupied:
            raise ValueError(f"Slot {self.id} is already occupied")
        self.occupied = True

    def release(self):
        if not self.occupied:
            raise ValueError(f"Slot {self.id} is already free")
        self.occupied = False

    def __str__(self):
        state = "occupied" if self.occupied else "free"
        return f"{self.id} [{self.slot_type.value}, {state}]"
