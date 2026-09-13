from datetime import datetime
from domain.ticket import Ticket
from domain.vehicle import Vehicle
from repository.pricing_rule_repository import PricingRuleRepository

class PricingService:
    def __init__(self, pricing_rule_repository: PricingRuleRepository):
        self._pricing_rule_repository = pricing_rule_repository

    def calculate_fee(self, ticket: Ticket) -> float:
        vehicle_type = Vehicle.VehicleType.CAR  # Default demo type
        rule = self._pricing_rule_repository.find_by_vehicle_type(vehicle_type)
        if not rule:
            raise ValueError(f"No pricing rule for {vehicle_type}")
        
        flat_fee = rule.flat_rate
        hourly_fee = self._calculate_hourly_fee(ticket, rule.rate_per_hour)
        return min(flat_fee, hourly_fee)

    def _calculate_hourly_fee(self, ticket: Ticket, rate_per_hour: float) -> float:
        duration = datetime.now() - ticket.entry_time
        hours = max(1, duration.total_seconds() // 3600)
        return hours * rate_per_hour
