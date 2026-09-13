from ..adapter.payment_gateway_adapter import PaymentGatewayAdapter
from ..adapter.razorpay_adapter import RazorpayAdapter
from ..adapter.stripe_adapter import StripeAdapter
from ..domain.payment import Payment
from ..repository.payment_repository import PaymentRepository

class PaymentService:
    def __init__(self, payment_repository: PaymentRepository):
        self._payment_repository = payment_repository
        self._default_gateway = RazorpayAdapter()
        print("[SERVICE] PaymentService initialized with default gateway: Razorpay")

    def process_payment(self, ticket_id: str, amount: float) -> bool:
        print(f"[SERVICE] Processing payment for ticket: {ticket_id} amount: {amount}")
        payment = Payment(ticket_id, amount, Payment.PaymentGateway.RAZORPAY)
        self._payment_repository.save(payment)
        
        success = self._default_gateway.pay(ticket_id, amount)
        if success:
            payment.mark_as_success()
        else:
            payment.mark_as_failed()
        
        self._payment_repository.update(payment)
        return success

    def process_payment_with_retry(self, ticket_id: str, amount: float, max_retries: int) -> bool:
        for i in range(1, max_retries + 1):
            print(f"[SERVICE] Payment attempt {i} of {max_retries}")
            if self.process_payment(ticket_id, amount):
                return True
            if i == 1:
                self._default_gateway = StripeAdapter()
                print("[SERVICE] Switching to Stripe gateway for retry")
        return False
