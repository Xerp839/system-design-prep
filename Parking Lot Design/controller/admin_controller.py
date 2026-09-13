from service.admin_service import AdminService
from domain.vehicle import Vehicle
from domain.pricing_rule import PricingRule

class AdminController:
    def __init__(self, admin_service: AdminService):
        self._admin_service = admin_service
        print("[CONTROLLER] AdminController initialized")

    def initialize_parking_lot(self):
        print("[CONTROLLER] Admin request to initialize parking lot")
        self._admin_service.initialize_parking_lot()

    def add_floor(self, floor_number: int):
        print(f"[CONTROLLER] Admin request to add floor: {floor_number}")
        self._admin_service.add_floor_public(floor_number)

    def add_slots_to_floor(self, floor_number: int, slot_type: Vehicle.VehicleType, count: int):
        print(f"[CONTROLLER] Admin request to add {count} {slot_type.value} slots to floor {floor_number}")
        self._admin_service.add_slots_to_floor_public(floor_number, slot_type, count)

    def update_pricing_rule(self, vehicle_type: Vehicle.VehicleType, rate_per_hour: float, flat_rate: float):
        print(f"[CONTROLLER] Admin request to update pricing for {vehicle_type.value}")
        self._admin_service.update_pricing_rule(vehicle_type, rate_per_hour, flat_rate)

    def get_parking_status(self):
        print("[CONTROLLER] Admin request to get parking status")
        return self._admin_service.get_parking_status()
