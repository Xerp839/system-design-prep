"""
Not interview code - you would not write tests in 45 minutes. This exists so the
repo proves the design works rather than asserting it.

Run:  python -m pytest tests -q     (from the "Parking Lot Design" folder)
"""

import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapter.payment_gateway import PaymentGatewayAdapter  # noqa: E402
from domain.payment import PaymentGateway, PaymentStatus  # noqa: E402
from domain.vehicle import VehicleType  # noqa: E402
from main import build_lot  # noqa: E402


class AlwaysPays(PaymentGatewayAdapter):
    def pay(self, ticket_id, amount):
        return True


class NeverPays(PaymentGatewayAdapter):
    def pay(self, ticket_id, amount):
        return False


@pytest.fixture
def lot():
    entry, exit_, slots = build_lot()
    return entry, exit_, slots


def test_entry_allocates_a_matching_slot(lot):
    entry, _, slots = lot
    before = slots.availability(VehicleType.CAR)[0]
    result = entry.enter_vehicle("KA-01-0001", VehicleType.CAR)

    assert result.success
    assert result.ticket_id and result.slot_id
    assert slots.availability(VehicleType.CAR)[0] == before - 1


def test_entry_fills_lowest_floor_first(lot):
    entry, _, _ = lot
    result = entry.enter_vehicle("KA-01-0002", VehicleType.CAR)
    assert result.slot_id.startswith("S-F0-")


def test_entry_fails_when_type_is_full(lot):
    entry, _, _ = lot
    for i in range(3):  # only 3 truck slots exist
        assert entry.enter_vehicle(f"TRK-{i}", VehicleType.TRUCK).success
    full = entry.enter_vehicle("TRK-X", VehicleType.TRUCK)

    assert not full.success
    assert "No free TRUCK slot" in full.message


def test_exit_charges_frees_the_slot_and_closes_the_ticket(lot):
    entry, exit_, slots = lot
    before = slots.availability(VehicleType.CAR)[0]
    ticket = entry.enter_vehicle("KA-01-0003", VehicleType.CAR)

    result = exit_.exit_vehicle(ticket.ticket_id)

    assert result.success
    assert result.fee == 20.0  # 1 hour minimum at the CAR rate
    assert slots.availability(VehicleType.CAR)[0] == before


def test_a_ticket_cannot_be_used_twice(lot):
    entry, exit_, _ = lot
    ticket = entry.enter_vehicle("KA-01-0004", VehicleType.CAR)
    exit_.exit_vehicle(ticket.ticket_id)

    assert exit_.exit_vehicle(ticket.ticket_id).message == "Ticket already used"


def test_unknown_ticket_is_rejected(lot):
    _, exit_, _ = lot
    assert exit_.exit_vehicle("T-does-not-exist").message == "Ticket not found"


def test_each_vehicle_type_is_priced_by_its_own_rule(lot):
    """The bug this guards: an earlier version billed every vehicle as a CAR."""
    entry, exit_, _ = lot
    bike = entry.enter_vehicle("KA-02-0001", VehicleType.BIKE)
    car = entry.enter_vehicle("KA-01-0005", VehicleType.CAR)

    assert exit_.exit_vehicle(bike.ticket_id).fee == 10.0
    assert exit_.exit_vehicle(car.ticket_id).fee == 20.0


def test_flat_rate_caps_a_long_stay(lot):
    entry, _, _ = lot
    from repository.pricing_rule_repository import PricingRuleRepository
    from domain.pricing_rule import PricingRule
    from service.pricing_service import PricingService
    from domain.ticket import Ticket

    repo = PricingRuleRepository()
    repo.save(PricingRule(VehicleType.CAR, rate_per_hour=20.0, flat_rate=60.0))
    pricing = PricingService(repo)

    ticket = Ticket("KA-01-0006", VehicleType.CAR, "S-F0-001")
    later = ticket.entry_time + timedelta(hours=10)

    # 10 hours x 20 = 200, capped at the 60 flat rate.
    assert pricing.calculate_fee(ticket, now=later) == 60.0


def test_payment_falls_back_to_the_second_gateway():
    from repository.payment_repository import PaymentRepository
    from service.payment_service import PaymentService

    repo = PaymentRepository()
    service = PaymentService(
        repo,
        gateways=[
            (PaymentGateway.RAZORPAY, NeverPays()),
            (PaymentGateway.STRIPE, AlwaysPays()),
        ],
    )

    assert service.process_payment("T-1", 20.0) is True

    attempts = repo.find_by_ticket_id("T-1")
    assert [p.status for p in attempts] == [PaymentStatus.FAILED, PaymentStatus.SUCCESS]
    assert [p.gateway for p in attempts] == [PaymentGateway.RAZORPAY, PaymentGateway.STRIPE]


def test_failed_payment_keeps_the_slot_occupied(lot):
    """The car has not left, so the slot must not be freed."""
    from repository.payment_repository import PaymentRepository
    from service.payment_service import PaymentService

    entry, exit_, slots = lot
    ticket = entry.enter_vehicle("KA-01-0007", VehicleType.CAR)
    occupied = slots.availability(VehicleType.CAR)[0]

    exit_._payment_service = PaymentService(
        PaymentRepository(), gateways=[(PaymentGateway.RAZORPAY, NeverPays())]
    )
    result = exit_.exit_vehicle(ticket.ticket_id)

    assert not result.success
    assert result.message == "Payment failed"
    assert slots.availability(VehicleType.CAR)[0] == occupied


def test_a_slot_cannot_be_double_booked(lot):
    _, _, slots = lot
    slot = slots.allocate_slot(VehicleType.TRUCK)
    with pytest.raises(ValueError, match="already occupied"):
        slot.occupy()
