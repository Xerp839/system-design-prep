import uuid
from enum import Enum

class Payment:
    """
    Payment Domain Model
    
    Represents a payment transaction for a parking ticket.
    """
    class PaymentGateway(Enum):
        RAZORPAY = "RAZORPAY"
        STRIPE = "STRIPE"

    class PaymentStatus(Enum):
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    def __init__(self, ticket_id: str, amount: float, gateway: PaymentGateway):
        self.id = str(uuid.uuid4())
        self.ticket_id = ticket_id
        self.amount = amount
        self.gateway = gateway
        self.status = self.PaymentStatus.PENDING

    def mark_as_success(self):
        self.status = self.PaymentStatus.SUCCESS

    def mark_as_failed(self):
        self.status = self.PaymentStatus.FAILED

    def __str__(self):
        return f"Payment(id={self.id}, ticket={self.ticket_id}, amount={self.amount}, status={self.status.value})"
