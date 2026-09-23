from .vehicle import VehicleType
from datetime import datetime
import itertools

class Ticket:


    _counter = itertools.count(1)
    def __init__(self, LicencePlate: str, VehicleType: VehicleType, slotid: str):
        self.id = f"T-{next(Ticket._counter)}"
        self.licence_plate = LicencePlate
        self.vehicle_type =  VehicleType
        self.slot_id = slotid
        self.entry_time = datetime.now()
        self.active = True

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"{self.id} {self.licence_plate} -> {self.slot_id}"