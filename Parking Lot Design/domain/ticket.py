import uuid
from datetime import datetime

class Ticket:
    """
    Ticket Domain Model
    
    Issued at vehicle entry. Tracks vehicle/slot association and entry time.
    """
    def __init__(self, vehicle_id: str, slot_id: str):
        self.id = str(uuid.uuid4())
        self.vehicle_id = vehicle_id
        self.slot_id = slot_id
        self.entry_time = datetime.now()
        self.active = True

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"Ticket(id={self.id}, vehicle={self.vehicle_id}, slot={self.slot_id}, active={self.active})"
