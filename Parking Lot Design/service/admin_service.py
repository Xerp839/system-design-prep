from ..domain.floor import Floor
from ..domain.parking_slot import ParkingSlot
from ..domain.pricing_rule import PricingRule
from ..domain.vehicle import Vehicle
from ..repository.floor_repository import FloorRepository
from ..repository.slot_repository import SlotRepository
from ..repository.pricing_rule_repository import PricingRuleRepository

class AdminService:
    def __init__(self, floor_repository: FloorRepository, slot_repository: SlotRepository, pricing_rule_repository: PricingRuleRepository):
        self._floor_repository = floor_repository
        self._slot_repository = slot_repository
        self._pricing_rule_repository = pricing_rule_repository
        print("[SERVICE] AdminService initialized")

    def initialize_parking_lot(self):
        print("[SERVICE] Initializing parking lot with default configuration")
        for i in range(3):
            self._add_floor(i)
        
        self._add_slots_to_floor(0, Vehicle.VehicleType.BIKE, 20)
        self._add_slots_to_floor(0, Vehicle.VehicleType.CAR, 30)
        self._add_slots_to_floor(0, Vehicle.VehicleType.TRUCK, 5)
        
        self._add_slots_to_floor(1, Vehicle.VehicleType.CAR, 40)
        self._add_slots_to_floor(1, Vehicle.VehicleType.EV, 10)
        
        self._add_slots_to_floor(2, Vehicle.VehicleType.CAR, 35)
        self._add_slots_to_floor(2, Vehicle.VehicleType.EV, 15)
        
        self._initialize_default_pricing_rules()
        print("[SERVICE] Parking lot initialization completed")

    def _add_floor(self, floor_number: int):
        if self._floor_repository.exists_by_number(floor_number):
            return
        floor = Floor(floor_number)
        self._floor_repository.save(floor)

    def _add_slots_to_floor(self, floor_number: int, slot_type: Vehicle.VehicleType, count: int):
        floor = self._floor_repository.find_by_number(floor_number)
        if not floor:
            return
        for _ in range(count):
            slot = ParkingSlot(slot_type, floor_number)
            self._slot_repository.save(slot)
            floor.add_slot(slot)

    def _initialize_default_pricing_rules(self):
        self._pricing_rule_repository.save(PricingRule(Vehicle.VehicleType.BIKE, 10.0, 30.0))
        self._pricing_rule_repository.save(PricingRule(Vehicle.VehicleType.CAR, 20.0, 60.0))
        self._pricing_rule_repository.save(PricingRule(Vehicle.VehicleType.TRUCK, 30.0, 90.0))
        self._pricing_rule_repository.save(PricingRule(Vehicle.VehicleType.EV, 15.0, 45.0))

    def add_floor_public(self, floor_number: int):
        self._add_floor(floor_number)

    def add_slots_to_floor_public(self, floor_number: int, slot_type: Vehicle.VehicleType, count: int):
        self._add_slots_to_floor(floor_number, slot_type, count)

    def update_pricing_rule(self, vehicle_type: Vehicle.VehicleType, rate_per_hour: float, flat_rate: float):
        rule = self._pricing_rule_repository.find_by_vehicle_type(vehicle_type)
        if rule:
            rule.update_rates(rate_per_hour, flat_rate)
            self._pricing_rule_repository.update(rule)

    def get_parking_status(self):
        floors = self._floor_repository.find_all()
        slot_stats = self._slot_repository.get_slot_statistics()
        return {
            "total_floors": len(floors),
            "slot_statistics": slot_stats
        }
