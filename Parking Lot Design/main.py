"""
Parking lot - wiring and a runnable demo.

This file is the only place that knows concrete classes. Everything else receives its
dependencies through its constructor, so any piece can be swapped or faked in tests.

Run:  python main.py
"""

import sys

from adapter.payment_gateway import RazorpayAdapter, StripeAdapter
from controller.entry_controller import EntryController
from controller.exit_controller import ExitController
from domain.floor import Floor
from domain.payment import PaymentGateway
from domain.pricing_rule import PricingRule
from domain.vehicle import VehicleType
from repository.floor_repository import FloorRepository
from repository.payment_repository import PaymentRepository
from repository.pricing_rule_repository import PricingRuleRepository
from repository.receipt_repository import ReceiptRepository
from repository.ticket_repository import TicketRepository
from service.payment_service import PaymentService
from service.pricing_service import PricingService
from service.receipt_service import ReceiptService
from service.slot_service import SlotService
from service.ticket_service import TicketService

LAYOUT = {
    0: [(VehicleType.BIKE, 10), (VehicleType.CAR, 15), (VehicleType.TRUCK, 3)],
    1: [(VehicleType.CAR, 20), (VehicleType.EV, 5)],
}

PRICES = [
    PricingRule(VehicleType.BIKE, rate_per_hour=10.0, flat_rate=30.0),
    PricingRule(VehicleType.CAR, rate_per_hour=20.0, flat_rate=60.0),
    PricingRule(VehicleType.TRUCK, rate_per_hour=30.0, flat_rate=90.0),
    PricingRule(VehicleType.EV, rate_per_hour=15.0, flat_rate=45.0),
]


def build_lot():
    """Wire everything up and seed the lot. Returns the two controllers."""
    floor_repo = FloorRepository()
    ticket_repo = TicketRepository()
    pricing_repo = PricingRuleRepository()
    payment_repo = PaymentRepository()
    receipt_repo = ReceiptRepository()

    # Seed: in a real system an admin screen does this. It is plain setup, not design,
    # so it lives here rather than in an admin service.
    for floor_number, spec in LAYOUT.items():
        floor = Floor(floor_number)
        for slot_type, count in spec:
            floor.add_slots(slot_type, count)
        floor_repo.save(floor)
    for rule in PRICES:
        pricing_repo.save(rule)

    slot_service = SlotService(floor_repo)
    ticket_service = TicketService(ticket_repo)
    pricing_service = PricingService(pricing_repo)
    receipt_service = ReceiptService(receipt_repo)
    payment_service = PaymentService(
        payment_repo,
        gateways=[
            (PaymentGateway.RAZORPAY, RazorpayAdapter()),
            (PaymentGateway.STRIPE, StripeAdapter()),
        ],
    )

    entry = EntryController(slot_service, ticket_service)
    exit_ = ExitController(
        ticket_service, pricing_service, payment_service, receipt_service, slot_service
    )
    return entry, exit_, slot_service


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    entry, exit_, slots = build_lot()

    print("=== PARKING LOT ===")
    print("CAR availability per floor:", slots.availability(VehicleType.CAR))

    print("\n-- entry --")
    car = entry.enter_vehicle("KA-01-1234", VehicleType.CAR)
    bike = entry.enter_vehicle("KA-02-9999", VehicleType.BIKE)
    for r in (car, bike):
        print(f"  {r.message}: ticket={r.ticket_id} slot={r.slot_id}")
    print("CAR availability per floor:", slots.availability(VehicleType.CAR))

    print("\n-- exit --")
    result = exit_.exit_vehicle(car.ticket_id)
    print(f"  {result.message}: fee={result.fee:.2f} receipt={result.receipt_id}")
    print("CAR availability per floor:", slots.availability(VehicleType.CAR))

    print("\n-- same ticket again --")
    print(" ", exit_.exit_vehicle(car.ticket_id).message)


if __name__ == "__main__":
    main()
