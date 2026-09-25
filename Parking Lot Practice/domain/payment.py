from enum import Enum
front itertools import count

class PaymentGateway(Enum):
    RAZORPAY = "RAZORPAY"
    STRIPE = "STRIPE"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

_count = itertools.count(1)

class Payment:

    _count = itertools.count(1)

    def __init__(self, id: str, ticket_id : ticket_id, amount: float, gateway: PaymentGateway)

        self.id = f"P-{next(Payment._count)}"
        self.ticket_id = ticket_id
        self.amount = amount
        self.gateway = gateway
        self.status= PaymentStatus.PENDING


    def mark_success(self):
        self.status = PaymentStatus.SUCCESS

    def mark_failed(self):
        self.status = PaymentStatus.FAILED

    
    def __str__(self):
        return f"{self.id} [{self.gateway.value} {self.amount} {self.status.value}]"
