from typing import Dict, List

from domain.payment import Payment


class PaymentRepository:
    def __init__(self):
        self._payments: Dict[str, Payment] = {}

    def save(self, payment: Payment) -> Payment:
        self._payments[payment.id] = payment
        return payment

    def find_by_ticket_id(self, ticket_id: str) -> List[Payment]:
        # The audit trail: every attempt, including the failures.
        return [p for p in self._payments.values() if p.ticket_id == ticket_id]
