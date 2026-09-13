from domain.receipt import Receipt
from domain.ticket import Ticket
from repository.receipt_repository import ReceiptRepository


class ReceiptService:
    def __init__(self, receipt_repository: ReceiptRepository):
        self._receipt_repository = receipt_repository

    def issue_receipt(self, ticket: Ticket, fee: float) -> Receipt:
        return self._receipt_repository.save(Receipt(ticket.id, fee))
