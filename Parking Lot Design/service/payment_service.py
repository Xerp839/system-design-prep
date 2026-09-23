from typing import List, Tuple

from adapter.payment_gateway import PaymentGatewayAdapter
from domain.payment import Payment, PaymentGateway
from repository.payment_repository import PaymentRepository


class PaymentService:
    """
    Tries each gateway in turn. Every attempt is saved, failures included, so the
    payment history explains what happened.

    The chosen gateway is a LOCAL, never stored on self - otherwise one customer's
    failure would permanently switch the gateway for every customer after them.
    """

    def __init__(
        self,
        payment_repository: PaymentRepository,
        gateways: List[Tuple[PaymentGateway, PaymentGatewayAdapter]],
    ):
        self._payment_repository = payment_repository
        self._gateways = gateways

    def process_payment(self, ticket_id: str, amount: float, max_attempts: int = 3) -> bool:
        for attempt in range(max_attempts):
            # Stay on the last gateway once we have run out of alternatives.
            gateway, adapter = self._gateways[min(attempt, len(self._gateways) - 1)]
            payment = self._payment_repository.save(Payment(ticket_id, amount, gateway))

            if adapter.pay(ticket_id, amount):
                payment.mark_success()
                return True
            payment.mark_failed()
        return False
