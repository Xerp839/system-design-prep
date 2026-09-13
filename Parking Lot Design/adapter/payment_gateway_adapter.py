from abc import ABC, abstractmethod

class PaymentGatewayAdapter(ABC):
    """
    PaymentGatewayAdapter Inteface
    
    Abstract base class for payment gateway adapters.
    """
    @abstractmethod
    def pay(self, ticket_id: str, amount: float) -> bool:
        pass
