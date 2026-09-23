from typing import NamedTuple, Optional

from service.payment_service import PaymentService
from service.pricing_service import PricingService
from service.receipt_service import ReceiptService
from service.slot_service import SlotService
from service.ticket_service import TicketService


class ExitResult(NamedTuple):
    success: bool
    receipt_id: Optional[str]
    fee: float
    message: str


class ExitController:
    def __init__(
        self,
        ticket_service: TicketService,
        pricing_service: PricingService,
        payment_service: PaymentService,
        receipt_service: ReceiptService,
        slot_service: SlotService,
    ):
        self._ticket_service = ticket_service
        self._pricing_service = pricing_service
        self._payment_service = payment_service
        self._receipt_service = receipt_service
        self._slot_service = slot_service

    def exit_vehicle(self, ticket_id: str) -> ExitResult:
        ticket = self._ticket_service.get_ticket(ticket_id)
        if not ticket:
            return ExitResult(False, None, 0.0, "Ticket not found")
        if not ticket.active:
            return ExitResult(False, None, 0.0, "Ticket already used")

        fee = self._pricing_service.calculate_fee(ticket)

        # Money first, slot second: if payment fails the car has not left, so the
        # slot must stay occupied.
        if not self._payment_service.process_payment(ticket_id, fee):
            return ExitResult(False, None, fee, "Payment failed")

        receipt = self._receipt_service.issue_receipt(ticket, fee)
        self._slot_service.release_slot(ticket.slot_id)
        self._ticket_service.close_ticket(ticket)
        return ExitResult(True, receipt.id, fee, "Exit successful")
