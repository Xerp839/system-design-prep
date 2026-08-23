from discount_strategy import DiscountStrategy

class DiscountService:
    def __init__(self, stretegy:DiscountStrategy) -> None:
        self.__strategy = stretegy

    def set_strategy(self, stretegy: DiscountStrategy) -> None:
        self.__strategy = stretegy

    def process(self):
        self.__strategy.calculate_discount()