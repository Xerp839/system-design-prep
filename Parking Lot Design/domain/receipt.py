import itertools
from datetime import datetime

from .payment import PaymentStatus


class Receipt:
    """
    Issued only after a payment succeeds, so it is born SUCCESS.
    There is no mark_as_paid step to forget.
    """

    _counter = itertools.count(1)

    def __init__(self, ticket_id: str, total_fee: float):
        self.id = f"R-{next(Receipt._counter)}"
        self.ticket_id = ticket_id
        self.total_fee = total_fee
        self.exit_time = datetime.now()
        self.payment_status = PaymentStatus.SUCCESS

    def __str__(self):
        return (
            f"{self.id} | ticket {self.ticket_id} | "
            f"fee {self.total_fee:.2f} | {self.payment_status.value}"
        )
