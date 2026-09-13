import random
from .payment_gateway_adapter import PaymentGatewayAdapter

class StripeAdapter(PaymentGatewayAdapter):
    """
    StripeAdapter
    
    Simulates payment via Stripe (85% success rate).
    """
    def pay(self, ticket_id: str, amount: float) -> bool:
        print(f"[ADAPTER] StripeAdapter processing payment for ticket: {ticket_id} amount: {amount}")
        success = random.random() < 0.85
        print(f"[ADAPTER] StripeAdapter payment result: {'SUCCESS' if success else 'FAILED'}")
        return success
