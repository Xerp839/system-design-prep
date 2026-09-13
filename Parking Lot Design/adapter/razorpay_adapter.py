import random
from .payment_gateway_adapter import PaymentGatewayAdapter

class RazorpayAdapter(PaymentGatewayAdapter):
    """
    RazorpayAdapter
    
    Simulates payment via Razorpay (90% success rate).
    """
    def pay(self, ticket_id: str, amount: float) -> bool:
        print(f"[ADAPTER] RazorpayAdapter processing payment for ticket: {ticket_id} amount: {amount}")
        success = random.random() < 0.9
        print(f"[ADAPTER] RazorpayAdapter payment result: {'SUCCESS' if success else 'FAILED'}")
        return success
