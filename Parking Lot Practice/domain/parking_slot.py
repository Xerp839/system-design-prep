from .vehicle import VehicleType

class ParkingSlot:

    def __init__(self, slotID: str ,slotType: VehicleType, floor : int,  occupied: bool):
        
        self.slot_type = slotType
        self.id = slotID
        self.floor_number = floor
        self.occupied = False

    
    def __str__(self):

        state = "occupied" if self.occupied else "free"
        return f"{self.id} [{self.slot_type.value} {state}]"