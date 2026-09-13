from typing import List, Optional, Dict
from ..domain.pricing_rule import PricingRule
from ..domain.vehicle import Vehicle

class PricingRuleRepository:
    def __init__(self):
        self._rules: Dict[str, PricingRule] = {}
        self._vehicle_type_to_rule: Dict[Vehicle.VehicleType, str] = {}

    def save(self, rule: PricingRule) -> PricingRule:
        self._rules[rule.id] = rule
        self._vehicle_type_to_rule[rule.vehicle_type] = rule.id
        return rule

    def find_by_id(self, rule_id: str) -> Optional[PricingRule]:
        return self._rules.get(rule_id)

    def find_by_vehicle_type(self, vehicle_type: Vehicle.VehicleType) -> Optional[PricingRule]:
        rule_id = self._vehicle_type_to_rule.get(vehicle_type)
        return self._rules.get(rule_id) if rule_id else None

    def find_all(self) -> List[PricingRule]:
        return list(self._rules.values())

    def update(self, rule: PricingRule):
        if rule.id in self._rules:
            self._rules[rule.id] = rule
            self._vehicle_type_to_rule[rule.vehicle_type] = rule.id

    def delete(self, rule_id: str):
        rule = self._rules.pop(rule_id, None)
        if rule:
            self._vehicle_type_to_rule.pop(rule.vehicle_type, None)

    def clear(self):
        self._rules.clear()
        self._vehicle_type_to_rule.clear()
