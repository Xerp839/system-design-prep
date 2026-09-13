from typing import List, Optional, Dict
from ..domain.payment import Payment

class PaymentRepository:
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
        self._ticket_to_payments: Dict[str, List[str]] = {}

    def save(self, payment: Payment) -> Payment:
        self._payments[payment.id] = payment
        if payment.ticket_id not in self._ticket_to_payments:
            self._ticket_to_payments[payment.ticket_id] = []
        self._ticket_to_payments[payment.ticket_id].append(payment.id)
        return payment

    def find_by_id(self, payment_id: str) -> Optional[Payment]:
        return self._payments.get(payment_id)

    def find_by_ticket_id(self, ticket_id: str) -> List[Payment]:
        payment_ids = self._ticket_to_payments.get(ticket_id, [])
        return [self._payments[pid] for pid in payment_ids if pid in self._payments]

    def find_all(self) -> List[Payment]:
        return list(self._payments.values())

    def update(self, payment: Payment):
        if payment.id in self._payments:
            self._payments[payment.id] = payment

    def delete(self, payment_id: str):
        payment = self._payments.pop(payment_id, None)
        if payment and payment.ticket_id in self._ticket_to_payments:
            self._ticket_to_payments[payment.ticket_id].remove(payment_id)

    def clear(self):
        self._payments.clear()
        self._ticket_to_payments.clear()
