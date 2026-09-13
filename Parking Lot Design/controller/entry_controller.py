from typing import NamedTuple, Optional
from service.slot_service import SlotService
from service.ticket_service import TicketService
from domain.vehicle import Vehicle

class EntryResult(NamedTuple):
    success: bool
    ticket_id: Optional[str]
    slot_id: Optional[str]
    message: str

class EntryController:
    def __init__(self, ticket_service: TicketService, slot_service: SlotService):
        self._ticket_service = ticket_service
        self._slot_service = slot_service
        print("[CONTROLLER] EntryController initialized")

    def enter_vehicle(self, license_plate: str, vehicle_type: Vehicle.VehicleType) -> EntryResult:
        print(f"[CONTROLLER] Vehicle entry request - License: {license_plate}, Type: {vehicle_type.value}")
        slot = self._slot_service.allocate_slot(vehicle_type)
        if not slot:
            return EntryResult(False, None, None, f"No available slots for {vehicle_type.value}")
        
        vehicle = Vehicle(license_plate, vehicle_type)
        ticket = self._ticket_service.generate_ticket(vehicle, slot.id)
        return EntryResult(True, ticket.id, slot.id, "Entry successful")
