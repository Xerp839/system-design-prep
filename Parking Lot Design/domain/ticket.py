import itertools
from datetime import datetime

from .vehicle import VehicleType


class Ticket:
    """
    Issued at entry, closed at exit.

    `vehicle_type` is copied onto the ticket on purpose. The ticket records what was
    agreed at entry, so pricing never has to go looking for the vehicle, and a later
    edit to the vehicle record cannot change an in-flight charge.
    """

    _counter = itertools.count(1)

    def __init__(self, license_plate: str, vehicle_type: VehicleType, slot_id: str):
        self.id = f"T-{next(Ticket._counter)}"
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.slot_id = slot_id
        self.entry_time = datetime.now()
        self.active = True

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"{self.id} [{self.license_plate} -> {self.slot_id}]"
