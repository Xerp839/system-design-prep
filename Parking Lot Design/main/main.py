import sys
import os

# Add the project root to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.vehicle import Vehicle
from repository.floor_repository import FloorRepository
from repository.slot_repository import SlotRepository
from repository.ticket_repository import TicketRepository
from repository.payment_repository import PaymentRepository
from repository.pricing_rule_repository import PricingRuleRepository
from service.admin_service import AdminService
from service.payment_service import Payment_Service # Re-checking class name
from service.payment_service import PaymentService
from service.pricing_service import PricingService
from service.receipt_service import ReceiptService
from service.slot_service import SlotService
from service.ticket_service import TicketService
from controller.admin_controller import AdminController
from controller.entry_controller import EntryController
from controller.exit_controller import ExitController

def main():
    print("=== PARKING LOT LLD SIMULATION (PYTHON) ===")
    
    # 1. Initialize Repositories
    floor_repo = FloorRepository()
    slot_repo = SlotRepository()
    ticket_repo = TicketRepository()
    payment_repo = PaymentRepository()
    pricing_repo = PricingRuleRepository()
    
    # 2. Initialize Services
    admin_service = AdminService(floor_repo, slot_repo, pricing_repo)
    payment_service = PaymentService(payment_repo)
    pricing_service = PricingService(pricing_repo)
    receipt_service = ReceiptService()
    slot_service = SlotService(slot_repo)
    ticket_service = TicketService(ticket_repo)
    
    # 3. Initialize Controllers
    admin_controller = AdminController(admin_service)
    entry_controller = EntryController(ticket_service, slot_service)
    exit_controller = ExitController(ticket_service, pricing_service, payment_service, receipt_service, slot_service)
    
    # 4. Initial Setup
    print("\n=== INITIALIZATION PHASE ===")
    admin_controller.initialize_parking_lot()
    
    # 5. Simulate Vehicle Entry
    print("\n=== ENTRY FLOW SIMULATION ===")
    res1 = entry_controller.enter_vehicle("ABC-123", Vehicle.VehicleType.CAR)
    if res1.success:
        print(f"✅ Entry successful - Ticket: {res1.ticket_id}")
        
    res2 = entry_controller.enter_vehicle("XYZ-789", Vehicle.VehicleType.BIKE)
    if res2.success:
        print(f"✅ Entry successful - Ticket: {res2.ticket_id}")
        
    # 6. Simulate Vehicle Exit
    print("\n=== EXIT FLOW SIMULATION ===")
    exit_res = exit_controller.exit_vehicle(res1.ticket_id)
    if exit_res.success:
        print(f"✅ Exit successful - Fee: ${exit_res.fee:.2f}")
        print(exit_controller.generate_receipt_text(res1.ticket_id))
        
    print("\n=== SIMULATION COMPLETED ===")

if __name__ == "__main__":
    main()
