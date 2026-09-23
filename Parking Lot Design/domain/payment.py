import itertools
from enum import Enum


class PaymentGateway(Enum):
    RAZORPAY = "RAZORPAY"
    STRIPE = "STRIPE"


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment:
    """One attempt to take money. A retried exit produces several of these."""

    _counter = itertools.count(1)

    def __init__(self, ticket_id: str, amount: float, gateway: PaymentGateway):
        self.id = f"P-{next(Payment._counter)}"
        self.ticket_id = ticket_id
        self.amount = amount
        self.gateway = gateway
        self.status = PaymentStatus.PENDING

    def mark_success(self):
        self.status = PaymentStatus.SUCCESS

    def mark_failed(self):
        self.status = PaymentStatus.FAILED

    def __str__(self):
        return f"{self.id} [{self.gateway.value} {self.amount} {self.status.value}]"
