import math
from datetime import datetime

from domain.ticket import Ticket
from repository.pricing_rule_repository import PricingRuleRepository


class PricingService:
    """
    Fee = cheaper of (hourly, flat). The flat rate acts as a daily cap, and the
    minimum charge is one hour.

    Money is a float here for brevity; production would use integer paise or Decimal.
    """

    def __init__(self, pricing_rule_repository: PricingRuleRepository):
        self._pricing_rule_repository = pricing_rule_repository

    def calculate_fee(self, ticket: Ticket, now: datetime = None) -> float:
        # `now` is injectable so tests can price a long stay without waiting for one.
        now = now or datetime.now()
        rule = self._pricing_rule_repository.find_by_vehicle_type(ticket.vehicle_type)
        if not rule:
            raise ValueError(f"No pricing rule for {ticket.vehicle_type.value}")

        hours = max(1, math.ceil((now - ticket.entry_time).total_seconds() / 3600))
        return min(rule.flat_rate, hours * rule.rate_per_hour)
