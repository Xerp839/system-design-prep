# 01 — Code Walkthrough

Read this with `Parking Lot Design/` open. I explain each layer bottom-up, because that's
the order the code actually depends on things.

> **This describes the refactored code.** The original copied version (597 lines, with an
> admin layer and a separate `SlotRepository`) is in git history on `main`. What changed and
> why is in `04-broken-things.md`.

Run it:

```
cd "Parking Lot Design"
python main.py
python -m pytest tests -q
```

---

## The mental model: 5 layers, calls flow down

```
main.py                     wiring + seed data + demo
   |
   v
controller/                 takes a request, returns a result. NO business logic.
   |
   v
service/                    the business rules live here. This is the brain.
   |
   v
repository/                 "where do I store and find things" (a fake DB, dict-based)
   |
   v
domain/                     the nouns: Vehicle, Floor, ParkingSlot, Ticket,
                            PricingRule, Payment, Receipt
```

Plus one sideways box:

```
adapter/                    talks to the outside world (Razorpay, Stripe)
```

**The rule that makes this work:** a layer may call *down*, never *up*.
`service` may import `repository`. `repository` must NEVER import `service`.
If you ever feel the urge to import upward, your logic is in the wrong layer.

**Size:** 421 lines of executable code, 34 methods, 20 files. That is roughly what you can
hand-write in 45 minutes. Everything in it is called by something.

---

## Layer 1 — `domain/` : the nouns

These are the things a *non-programmer* would name if you asked them to describe a parking
lot. That's the test for "is this a domain class."

### `vehicle.py`

```python
class VehicleType(Enum):
    BIKE = "BIKE"; CAR = "CAR"; TRUCK = "TRUCK"; EV = "EV"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
```

Three decisions worth saying out loud:

1. **The enum is at module level**, not nested inside `Vehicle`. Nested enums
   (`Vehicle.VehicleType.CAR`) are a Java habit; `VehicleType.CAR` is the Python idiom.
2. **Why an enum and not a string?** Because `"car"`, `"Car"`, `"CAR"` are three different
   strings and one of them will bite you at 2am. An enum makes the set of legal values
   *closed*. Always enum your types — interviewers notice immediately.
3. **`Vehicle` has no `id`.** The license plate *is* the identity — it's the natural key, it's
   already unique, and inventing a UUID beside it would mean maintaining two identities for
   one car. This is also why there's no `VehicleRepository`: nothing ever needs to look a
   vehicle up.

### `parking_slot.py`

```python
class ParkingSlot:
    def __init__(self, slot_id, slot_type, floor_number):
        self.id = slot_id                # "S-F0-011" — readable, not a UUID
        self.slot_type = slot_type
        self.floor_number = floor_number
        self.occupied = False

    def occupy(self):
        if self.occupied:
            raise ValueError(f"Slot {self.id} is already occupied")
        self.occupied = True

    def release(self):
        if not self.occupied:
            raise ValueError(f"Slot {self.id} is already free")
        self.occupied = False
```

A slot is a boolean with an address. But note the transition is **guarded**: nobody writes
`slot.occupied = True` from outside. That turns a double-booking — the exact bug concurrency
would cause — into a loud `ValueError` instead of a silent overwrite.

That's encapsulation doing real work, and it's a much better example to point at than a
getter.

### `floor.py`

```python
class Floor:
    def __init__(self, floor_number):
        self.floor_number = floor_number
        self.slots: List[ParkingSlot] = []

    def add_slots(self, slot_type, count):
        for _ in range(count):
            slot_id = f"S-F{self.floor_number}-{len(self.slots) + 1:03d}"
            self.slots.append(ParkingSlot(slot_id, slot_type, self.floor_number))

    def find_free_slot(self, vehicle_type):
        return next((s for s in self.slots
                     if s.slot_type == vehicle_type and not s.occupied), None)

    def available_count(self, vehicle_type):
        return sum(1 for s in self.slots
                   if s.slot_type == vehicle_type and not s.occupied)
```

**A floor owns its slots, and it is the only place slots live.** That matters more than it
looks: in the original code, slots existed *both* inside `Floor.slots` and inside a flat
`SlotRepository` dict. Two containers, one truth — and allocation only ever used the flat
one, so `Floor` was decorative. Deleting `SlotRepository` fixed that.

`available_count` is what an entrance display board would call. `main.py` prints it before
and after each entry, which is how you *show* the design works rather than claiming it.

### `ticket.py`

```python
class Ticket:
    _counter = itertools.count(1)

    def __init__(self, license_plate, vehicle_type, slot_id):
        self.id = f"T-{next(Ticket._counter)}"
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type    # copied on purpose — see below
        self.slot_id = slot_id
        self.entry_time = datetime.now()
        self.active = True

    def deactivate(self): self.active = False
```

**Why `vehicle_type` is copied onto the ticket.** This is the single most interesting
modelling decision in the project, and it's worth having an answer ready.

The alternative is storing `vehicle_id` and looking the vehicle up at exit — which is what
the original did, except it had no `VehicleRepository`, so `PricingService` gave up and
hardcoded `CAR`. Every bike was billed at car rates.

Copying the field ("denormalising") is not just the cheap fix, it's the *more correct* one:
**the ticket records what was agreed at entry.** If someone later edits the vehicle record,
an in-flight charge must not change. Receipts and invoices work this way in every real
billing system.

The general rule, which transfers to every other LLD problem:

> When you replace an object reference with an id, you owe yourself either a repository to
> resolve it, or a copy of the field you actually need. Pick one **deliberately**. The bug
> is picking neither.

Also note `itertools.count` for ids. `T-1`, `S-F0-011`, `R-1` make the demo output legible;
`35e063b3-374b-4551-bf29-cc1dce0829a9` does not. Say "UUIDs in production, readable ids so
you can see the flow."

### `pricing_rule.py`

```python
PricingRule(vehicle_type, rate_per_hour, flat_rate)
```

"For a CAR: 20/hour, or 60 flat." One rule per vehicle type. This is **data, not code** —
the point being that changing prices must never mean editing an `if/elif` chain.

### `payment.py` and `receipt.py`

```python
class PaymentGateway(Enum):  RAZORPAY, STRIPE
class PaymentStatus(Enum):   PENDING, SUCCESS, FAILED

class Payment:    # one ATTEMPT to take money
class Receipt:    # the DOCUMENT you hand over after one succeeded
```

One exit can produce three `Payment` rows and one `Receipt` — two failed retries and a
success. That's why they're separate classes, and it's a good answer when asked why.

`PaymentStatus` is defined once, in `payment.py`, and imported by `receipt.py`. The original
declared it twice, in both files, as two unrelated enums that could silently drift apart.

`Receipt` is born `SUCCESS` because it is only ever created after payment succeeds — there's
no `mark_as_paid()` step that someone can forget to call. **Make illegal states
unrepresentable** where it's cheap to do so.

---

## Layer 2 — `repository/` : fake database

Five repositories — floors, tickets, pricing rules, payments, receipts — each holding a dict
and exposing only the queries something actually calls.

```python
class TicketRepository:
    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}

    def save(self, ticket):      self._tickets[ticket.id] = ticket; return ticket
    def find_by_id(self, tid):   return self._tickets.get(tid)
```

**Why bother?** Three reasons, and you should be able to say all three:

1. **It's a seam.** Today it's a `dict`. Tomorrow it's Postgres. Only this file changes.
   Nothing in `service/` knows or cares. That's the Repository pattern, and also the
   Dependency Inversion Principle in practice.
2. **It names your queries.** `find_by_vehicle_type(CAR)` is a sentence; the same
   dict lookup scattered across three services is not.
3. **It gives you somewhere to put an index.** See below.

### `FloorRepository` — one source of truth plus an index

```python
class FloorRepository:
    def __init__(self):
        self._floors: List[Floor] = []
        self._slots_by_id: Dict[str, ParkingSlot] = {}   # index for O(1) release

    def save(self, floor):
        self._floors.append(floor)
        self.index_slots(floor)
        return floor

    def find_slot(self, slot_id):
        return self._slots_by_id.get(slot_id)
```

Slots live in exactly one place — inside their floor. The dict is an **index**, not a second
copy: same objects, keyed by id, so releasing a slot at exit is O(1) instead of walking every
floor. Mentioning that distinction ("index, not a copy") is free points.

### What is *not* here any more

`SlotRepository.allocate_slot()` used to find a free slot **and mutate it** in one method.
Find-and-mutate is a *policy* decision (which slot do we hand out?) living in the storage
layer. It moved to `SlotService`, where policy belongs.

---

## Layer 3 — `service/` : the brain

A service takes repositories in its constructor and implements one verb of the business.

### `slot_service.py` — allocation policy, and the concurrency answer

```python
class SlotService:
    def __init__(self, floor_repository):
        self._floor_repository = floor_repository
        self._lock = threading.Lock()

    def allocate_slot(self, vehicle_type):
        with self._lock:
            for floor in sorted(self._floor_repository.find_all(),
                                key=lambda f: f.floor_number):
                slot = floor.find_free_slot(vehicle_type)
                if slot:
                    slot.occupy()
                    return slot
            return None
```

Two things to say about this method, both of which interviewers reach for:

**The policy is explicit and isolated.** Today: lowest floor first, first free slot on it.
Nearest-to-exit, cheapest-floor, or spread-the-load are all *this method* and nothing else.

**The lock is the concurrency answer.** `find_free_slot` then `occupy()` is read-then-write —
two gates can otherwise win the same slot. The comment in the code says what the real fix is:

```python
# In a real DB this becomes UPDATE ... WHERE id=? AND occupied=false
```

Raise this before they ask. It is the number-one follow-up in a parking-lot interview.

### `pricing_service.py` — the interesting business rule

```python
def calculate_fee(self, ticket, now=None):
    now = now or datetime.now()
    rule = self._pricing_rule_repository.find_by_vehicle_type(ticket.vehicle_type)
    if not rule:
        raise ValueError(f"No pricing rule for {ticket.vehicle_type.value}")
    hours = max(1, math.ceil((now - ticket.entry_time).total_seconds() / 3600))
    return min(rule.flat_rate, hours * rule.rate_per_hour)
```

Three real-world behaviours in two lines:

- `math.ceil` — part-hours round **up**, like every real car park. (The original used `//`,
  which truncates: 61 minutes billed as one hour.)
- `max(1, ...)` — a minimum charge of one hour.
- `min(flat, hourly)` — the flat rate acts as a **daily cap**.

`now` is a parameter with a default. That's not decoration: it makes the function pure and
lets a test price a ten-hour stay without waiting ten hours. `test_flat_rate_caps_a_long_stay`
does exactly that. If asked about the "system clock mismatch" edge case, this is your hook —
inject a clock instead of calling `datetime.now()` in five places.

Money is `float` here for brevity. **Say so before they ask:** production uses integer paise
or `Decimal`, because floats accumulate rounding error on money.

### `payment_service.py` — retries and gateway fallback

```python
def process_payment(self, ticket_id, amount, max_attempts=3):
    for attempt in range(max_attempts):
        gateway, adapter = self._gateways[min(attempt, len(self._gateways) - 1)]
        payment = self._payment_repository.save(Payment(ticket_id, amount, gateway))
        if adapter.pay(ticket_id, amount):
            payment.mark_success()
            return True
        payment.mark_failed()
    return False
```

Try Razorpay; if it fails, try Stripe; stay on the last gateway once alternatives run out.
Every attempt is saved, failures included, so the payment history explains what happened.

**The chosen gateway is a local variable, never stored on `self`.** The original assigned
`self._default_gateway = StripeAdapter()` on failure, so one customer's failed card
permanently switched the gateway for every customer after them — and the saved `Payment` row
still said `RAZORPAY`, so the audit trail lied. Mutable state on a long-lived service is how
one request poisons the next.

The gateway list is **injected**, which is what makes
`test_payment_falls_back_to_the_second_gateway` possible with no network.

---

## Layer 4 — `adapter/` : the outside world

```python
class PaymentGatewayAdapter(ABC):
    @abstractmethod
    def pay(self, ticket_id: str, amount: float) -> bool: ...

class RazorpayAdapter(PaymentGatewayAdapter): ...
class StripeAdapter(PaymentGatewayAdapter): ...
```

**This is the whole Adapter pattern, and it's the highest value-per-line in the project.**

Razorpay's real SDK has something like `razorpay.Order.create(...)`; Stripe's has
`stripe.PaymentIntent.create(...)`. Different names, arguments, return shapes. Each adapter
wraps one of them behind a single interface — `pay() -> bool` — that **you** defined for
**your** needs, not the one a vendor shipped.

Consequences worth saying out loud:

- `PaymentService` depends on the abstract class, never on Razorpay → **Dependency Inversion**.
- Adding PayPal is one new class, zero edits elsewhere → **Open/Closed**.
- Tests pass an `AlwaysPays` / `NeverPays` fake. No network. See `tests/test_flows.py`.

---

## Layer 5 — `controller/` : the door

```python
def enter_vehicle(self, license_plate, vehicle_type) -> EntryResult:
    slot = self._slot_service.allocate_slot(vehicle_type)
    if not slot:
        return EntryResult(False, None, None, f"No free {vehicle_type.value} slot")
    try:
        vehicle = Vehicle(license_plate, vehicle_type)
        ticket = self._ticket_service.generate_ticket(vehicle, slot.id)
    except Exception:
        self._slot_service.release_slot(slot.id)   # compensating action
        raise
    return EntryResult(True, ticket.id, slot.id, "Entry successful")
```

A controller does exactly four things: accept primitives, call services **in order**, turn
failure into a *message* rather than an exception, and return a **result object**.

```python
class EntryResult(NamedTuple):
    success: bool; ticket_id: Optional[str]; slot_id: Optional[str]; message: str
```

Why a result object instead of the `Ticket`? So the caller needn't know your internals, and
so failure is *data* rather than an exception someone forgot to catch. In a web app this is
literally your JSON response body.

**The `try/except` is the interesting part.** The slot is already occupied by the time we
build the ticket. If that throws, the slot would stay occupied forever with no ticket able to
free it. So we hand it back. In a real system this is one database transaction; here it's a
compensating action. The general question to ask yourself every time: *"I've just mutated
shared state — what if the next line fails?"*

### `exit_controller.py` — the ordering that matters

```python
ticket = self._ticket_service.get_ticket(ticket_id)
if not ticket:       return ExitResult(False, None, 0.0, "Ticket not found")
if not ticket.active: return ExitResult(False, None, 0.0, "Ticket already used")

fee = self._pricing_service.calculate_fee(ticket)
if not self._payment_service.process_payment(ticket_id, fee):
    return ExitResult(False, None, fee, "Payment failed")

receipt = self._receipt_service.issue_receipt(ticket, fee)
self._slot_service.release_slot(ticket.slot_id)
self._ticket_service.close_ticket(ticket)
return ExitResult(True, receipt.id, fee, "Exit successful")
```

**Take money first, free the slot second.** If payment fails we return early and the slot
stays occupied, because the car physically hasn't left. That ordering *is* the design, it's
covered by `test_failed_payment_keeps_the_slot_occupied`, and if an interviewer asks one deep
question about your exit flow it will be this one.

The `ticket.active` guard is what makes a ticket single-use — try the same ticket twice and
you get "Ticket already used" instead of a free slot leak and a second charge.

---

## Layer 0 — `main.py` : wiring and seed

```python
def build_lot():
    floor_repo = FloorRepository(); ticket_repo = TicketRepository(); ...
    for floor_number, spec in LAYOUT.items():
        floor = Floor(floor_number)
        for slot_type, count in spec:
            floor.add_slots(slot_type, count)
        floor_repo.save(floor)
    ...
    return entry, exit_, slot_service
```

Nothing constructs its own dependencies — everything arrives through a constructor. That's
**Dependency Injection**, and `main` is the one place allowed to know concrete types. In
Spring or Django a framework does this; in an interview you do it by hand and say "a DI
container wires this in production."

`build_lot()` is a function rather than inline code so the tests can call it too — one
wiring definition, used by both the demo and the test suite.

**The seed data replaced an entire admin layer.** The original had `AdminService` +
`AdminController` + a third repository — 108 lines — to create three floors and four prices.
Here it's a dict and a loop. Admin CRUD is the correct thing to cut under time pressure;
you *describe* it instead.

---

## The two flows, end to end

**Entry**

```
main -> EntryController.enter_vehicle("KA-01-1234", CAR)
     -> SlotService.allocate_slot(CAR)      [lock]
          -> floors in order -> Floor.find_free_slot -> slot.occupy()
     -> TicketService.generate_ticket(vehicle, slot.id)
          -> Ticket(plate, type, slot_id, entry_time=now) -> save
     <- EntryResult(success=True, ticket_id="T-1", slot_id="S-F0-011")
```

**Exit**

```
main -> ExitController.exit_vehicle("T-1")
     -> TicketService.get_ticket              (guard: exists? active?)
     -> PricingService.calculate_fee          (ceil hours, min(flat, hourly))
     -> PaymentService.process_payment        (Razorpay -> Stripe, every attempt saved)
     -> ReceiptService.issue_receipt          (born SUCCESS, saved)
     -> SlotService.release_slot              [lock] -> slot.release()
     -> TicketService.close_ticket            (active = False)
     <- ExitResult(success=True, receipt_id="R-1", fee=20.0)
```

**If you can draw those two ladders from memory, you understand this design.** Everything
else is muscle memory, and `02-build-order.md` is how you build it.

---

## `tests/` — not interview code

Eleven tests, 111 lines. You would **not** write these in a 45-minute interview, and they're
excluded from the line count above. They exist so this repo *proves* the design works rather
than asserting it, and each one documents a decision:

| Test | The decision it pins down |
| :--- | :--- |
| `test_entry_fills_lowest_floor_first` | allocation policy is real and observable |
| `test_entry_fails_when_type_is_full` | a full lot is a message, not a crash |
| `test_each_vehicle_type_is_priced_by_its_own_rule` | guards the old hardcoded-`CAR` bug |
| `test_flat_rate_caps_a_long_stay` | the daily cap, via an injected `now` |
| `test_payment_falls_back_to_the_second_gateway` | retry order + audit trail |
| `test_failed_payment_keeps_the_slot_occupied` | the money-before-slot ordering |
| `test_a_ticket_cannot_be_used_twice` | single-use tickets |
| `test_a_slot_cannot_be_double_booked` | the guarded state transition |

If you're showing this folder to someone, the test file is the most persuasive thing in it.
