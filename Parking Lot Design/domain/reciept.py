import uuid
from enum import Enum
from datetime import datetime

class Receipt:
    """
    Receipt Domain Model
    
    Issued at vehicle exit after payment.
    """
    class PaymentStatus(Enum):
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    def __init__(self, ticket_id: str, total_fee: float):
        self.id = str(uuid.uuid4())
        self.ticket_id = ticket_id
        self.exit_time = datetime.now()
        self.total_fee = total_fee
        self.payment_status = self.PaymentStatus.PENDING

    def mark_as_paid(self):
        self.payment_status = self.PaymentStatus.SUCCESS

    def __str__(self):
        return f"Receipt(id={self.id}, ticket={self.ticket_id}, fee={self.total_fee}, status={self.payment_status.value})"
