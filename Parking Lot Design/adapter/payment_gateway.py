import random
from abc import ABC, abstractmethod


class PaymentGatewayAdapter(ABC):
    """
    The interface WE need, not the one a vendor ships.

    Razorpay and Stripe have different SDKs, arguments and return shapes. Each adapter
    hides one of them behind this single method, so PaymentService never imports a
    vendor. Adding PayPal is a new class here and no edit anywhere else.
    """

    @abstractmethod
    def pay(self, ticket_id: str, amount: float) -> bool:
        ...


class RazorpayAdapter(PaymentGatewayAdapter):
    def pay(self, ticket_id: str, amount: float) -> bool:
        success = random.random() < 0.9  # stand-in for a real API call
        print(f"  [razorpay] {ticket_id} {amount:.2f} -> {'ok' if success else 'failed'}")
        return success


class StripeAdapter(PaymentGatewayAdapter):
    def pay(self, ticket_id: str, amount: float) -> bool:
        success = random.random() < 0.85
        print(f"  [stripe]   {ticket_id} {amount:.2f} -> {'ok' if success else 'failed'}")
        return success
