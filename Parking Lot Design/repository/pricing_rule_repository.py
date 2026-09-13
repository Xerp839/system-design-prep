from typing import Dict, Optional

from domain.pricing_rule import PricingRule
from domain.vehicle import VehicleType


class PricingRuleRepository:
    def __init__(self):
        self._rules: Dict[VehicleType, PricingRule] = {}

    def save(self, rule: PricingRule) -> PricingRule:
        self._rules[rule.vehicle_type] = rule
        return rule

    def find_by_vehicle_type(self, vehicle_type: VehicleType) -> Optional[PricingRule]:
        return self._rules.get(vehicle_type)
