from typing import NamedTuple, Optional

from domain.vehicle import Vehicle, VehicleType
from service.slot_service import SlotService
from service.ticket_service import TicketService


class EntryResult(NamedTuple):
    success: bool
    ticket_id: Optional[str]
    slot_id: Optional[str]
    message: str


class EntryController:
    def __init__(self, slot_service: SlotService, ticket_service: TicketService):
        self._slot_service = slot_service
        self._ticket_service = ticket_service

    def enter_vehicle(self, license_plate: str, vehicle_type: VehicleType) -> EntryResult:
        slot = self._slot_service.allocate_slot(vehicle_type)
        if not slot:
            return EntryResult(False, None, None, f"No free {vehicle_type.value} slot")

        try:
            vehicle = Vehicle(license_plate, vehicle_type)
            ticket = self._ticket_service.generate_ticket(vehicle, slot.id)
        except Exception:
            # The slot is already occupied at this point. If we cannot issue the
            # ticket, hand it back - otherwise it is occupied with nothing to free it.
            self._slot_service.release_slot(slot.id)
            raise

        return EntryResult(True, ticket.id, slot.id, "Entry successful")
