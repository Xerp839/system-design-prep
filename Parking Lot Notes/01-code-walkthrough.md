# 01 — Code Walkthrough

Read this with `Parking Lot Design/` open. I explain each layer bottom-up, because that's
the order the code actually depends on things.

---

## The mental model: 5 layers, calls flow down

```
main.py                     "the driver / the client"
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
domain/                     the nouns: Vehicle, Ticket, Slot, Floor, Payment, Receipt
```

Plus one sideways box:

```
adapter/                    talks to the outside world (Razorpay, Stripe)
```

**The rule that makes this work:** a layer may call *down*, never *up*.
`service` may import `repository`. `repository` must NEVER import `service`.
If you ever feel the urge to import upward, your logic is in the wrong layer.

---

## Layer 1 — `domain/` : the nouns

These are the things a *non-programmer* would name if you asked them to describe a parking lot.
That's the test for "is this a domain class."

### `vehicle.py`

```python
class Vehicle:
    class VehicleType(Enum):
        BIKE = "BIKE"; CAR = "CAR"; TRUCK = "TRUCK"; EV = "EV"

    def __init__(self, license_plate, vehicle_type):
        self.id = str(uuid.uuid4())
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
```

Two things worth noticing:

1. **The enum is nested inside the class** — `Vehicle.VehicleType.CAR`. This is a Java habit
   carried into Python. Idiomatic Python would put `class VehicleType(Enum)` at module level
   and write `VehicleType.CAR`. Either is fine in an interview — just be consistent.
2. **Why an enum and not a string?** Because `"car"`, `"Car"`, `"CAR"` are three different
   strings and one of them will bite you at 2am. An enum makes the set of legal values
   *closed*. Interviewers notice this immediately. Always enum your types.

### `parking_slot.py`

```python
class ParkingSlot:
    def __init__(self, slot_type, floor_number):
        self.id = str(uuid.uuid4())
        self.slot_type = slot_type       # a VehicleType — which vehicles fit here
        self.occupied = False            # the ONLY mutable state that matters
        self.floor_number = floor_number
```

A slot is basically a boolean with an address. `slot_type` being a `VehicleType` encodes
the rule "a CAR slot takes a CAR." (A richer design would let a car park in a truck slot —
see `04-broken-things.md`.)

### `floor.py`

```python
class Floor:
    def __init__(self, floor_number):
        self.id = ...; self.floor_number = floor_number
        self.slots: List[ParkingSlot] = []

    def add_slot(self, slot): self.slots.append(slot)

    def get_available_slots(self, vehicle_type):
        return [s for s in self.slots if s.slot_type == vehicle_type and not s.occupied]
```

**A Floor is a container.** Note it has *behaviour*, not just data. That's encapsulation:
the floor answers questions about itself rather than letting outsiders loop over
`floor.slots` by hand. When the interviewer says "apply OOP principles," this tiny method
is something you can point at.

### `ticket.py`

```python
class Ticket:
    def __init__(self, vehicle_id, slot_id):
        self.id = ...
        self.vehicle_id = vehicle_id     # NOTE: an id, not the Vehicle object
        self.slot_id = slot_id
        self.entry_time = datetime.now() # the thing we bill from
        self.active = True               # flips False at exit

    def deactivate(self): self.active = False
```

Two design decisions baked in here:

- **It stores IDs, not objects.** This mimics how a real database row works (foreign keys)
  and stops you from building one giant object graph where everything points at everything.
  The cost: you now need a repository to turn an id back into an object. That cost is real,
  and this codebase **fails to pay it** — there is no `VehicleRepository`, which is exactly
  why `PricingService` ends up hardcoding `CAR`.
- **`active` is the lifecycle flag.** One ticket = one parking session. You don't delete the
  ticket at exit, you deactivate it, so you keep history.

### `pricing_rule.py`

```python
PricingRule(vehicle_type, rate_per_hour, flat_rate)
```

"For a CAR: 20/hour, or 60 flat." One rule per vehicle type. This is **data, not code** —
which is the point. Changing prices must not mean editing an `if/elif` chain.

### `payment.py` and `reciept.py`

- `Payment` = the *attempt* to take money (`PENDING/SUCCESS/FAILED`, a gateway, an amount).
- `Receipt` = the *document* you hand the driver after it worked (exit time, total fee).

You can have 3 Payment rows and 1 Receipt for the same exit — two failed retries and a
success. That's why they're separate classes. Interviewers like it when you justify that split.

> The file is spelled `reciept.py` but the class is `Receipt`, and two other files try to
> import `receipt.py`. That's one of the reasons the code doesn't run.

---

## Layer 2 — `repository/` : fake database

Every repository is the same shape:

```python
class TicketRepository:
    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}     # the "table", keyed by id

    def save(self, ticket):        self._tickets[ticket.id] = ticket; return ticket
    def find_by_id(self, tid):     return self._tickets.get(tid)
    def find_active_tickets(self): return [t for t in self._tickets.values() if t.active]
```

**Why bother?** Three reasons, and you should be able to say all three:

1. **It's a seam.** Today it's a `dict`. Tomorrow it's Postgres. Only this file changes.
   Nothing in `service/` knows or cares. That's the Repository pattern, and also the
   Dependency Inversion Principle in practice.
2. **It names your queries.** `find_available_slots(vehicle_type)` is a sentence.
   Scattering that list-comprehension across five services is not.
3. **It gives you somewhere to put indexes.** Look at `FloorRepository`:

```python
self._floors: Dict[str, Floor] = {}              # primary key
self._floor_number_to_id: Dict[int, str] = {}    # secondary index
```

Two dicts, so `find_by_number(2)` is O(1) instead of a scan. Same trick in
`PaymentRepository` (`_ticket_to_payments`) and `PricingRuleRepository`
(`_vehicle_type_to_rule`). **Mentioning this in an interview is free points** — it shows
you're thinking about access patterns, which is the bridge from LLD to HLD.

### The one repository that cheats: `SlotRepository`

```python
def allocate_slot(self, vehicle_type):
    for slot in self._slots.values():
        if slot.slot_type == vehicle_type and not slot.occupied:
            slot.occupied = True          # <-- mutating state, inside a repository
            return slot
    return None
```

Find-and-mutate in one method. Strictly, "which slot do we pick" is a *business* decision
(nearest to the gate? cheapest floor?) and belongs in `SlotService`. It's here because in a
real DB you'd want this to be one atomic `UPDATE ... WHERE occupied = false LIMIT 1` so two
cars can't win the same slot. That's a defensible reason — but *say it out loud*, don't let
the interviewer assume you put it there by accident.

---

## Layer 3 — `service/` : the brain

A service takes repositories in its constructor and implements one verb of the business.

### `slot_service.py`, `ticket_service.py` — thin, and that's OK

```python
class TicketService:
    def __init__(self, ticket_repository):
        self._ticket_repository = ticket_repository

    def generate_ticket(self, vehicle, slot_id):
        ticket = Ticket(vehicle.id, slot_id)
        return self._ticket_repository.save(ticket)
```

Right now this is a one-line pass-through and it *feels* pointless. It isn't: it's the place
"issue a ticket" will grow into when you add validation, a QR code, an SMS. Don't apologise
for thin services — say "this is thin today, here's what would live here."

### `pricing_service.py` — the interesting one

```python
def calculate_fee(self, ticket):
    vehicle_type = Vehicle.VehicleType.CAR  # Default demo type   <-- BUG, see 04
    rule = self._pricing_rule_repository.find_by_vehicle_type(vehicle_type)
    flat_fee   = rule.flat_rate
    hourly_fee = self._calculate_hourly_fee(ticket, rule.rate_per_hour)
    return min(flat_fee, hourly_fee)        # cheaper of the two

def _calculate_hourly_fee(self, ticket, rate_per_hour):
    duration = datetime.now() - ticket.entry_time
    hours = max(1, duration.total_seconds() // 3600)   # minimum 1 hour billed
    return hours * rate_per_hour
```

Read that `min(flat, hourly)` carefully — it's the actual business rule: *park long enough
and you hit a daily cap.* And `max(1, ...)` is the *minimum charge*. Two real-world pricing
behaviours in three lines. This is what "business logic" means, and why it can't live in a
controller or a repository.

The hardcoded `CAR` is a genuine bug: the ticket stores `vehicle_id`, there is no
`VehicleRepository`, so the service literally cannot find out what kind of vehicle this is.
The author papered over it. You will fix it.

### `payment_service.py` — retries and gateway fallback

```python
def process_payment_with_retry(self, ticket_id, amount, max_retries):
    for i in range(1, max_retries + 1):
        if self.process_payment(ticket_id, amount): return True
        if i == 1:
            self._default_gateway = StripeAdapter()   # fall back to another provider
    return False
```

Try Razorpay; if the first attempt fails, switch to Stripe and keep trying. Each attempt
creates and saves a `Payment` row, so you have an audit trail of failures. (It has a bug —
it mutates `self._default_gateway` permanently, so the *next* customer never sees Razorpay.
See `04-broken-things.md`.)

### `admin_service.py` — setup

`initialize_parking_lot()` builds 3 floors, ~155 slots, and 4 pricing rules. It's seed data.
Note the `_add_floor` / `add_floor_public` pair — that's Java's private/public transliterated
into Python, and it's noise. In Python, just have one public `add_floor`.

---

## Layer 4 — `adapter/` : the outside world

```python
class PaymentGatewayAdapter(ABC):
    @abstractmethod
    def pay(self, ticket_id: str, amount: float) -> bool: ...

class RazorpayAdapter(PaymentGatewayAdapter):
    def pay(self, ticket_id, amount): return random.random() < 0.9

class StripeAdapter(PaymentGatewayAdapter):
    def pay(self, ticket_id, amount): return random.random() < 0.85
```

**This is the whole Adapter pattern, and it's the most important 10 lines in the project.**

Razorpay's real SDK has some method like `razorpay.Order.create(...)`. Stripe's has
`stripe.PaymentIntent.create(...)`. Different names, different arguments, different return
shapes. The adapter *wraps* each one behind a single interface — `pay() -> bool` — that
**you** defined for **your** needs.

Consequences worth saying out loud:

- `PaymentService` depends on the abstract `PaymentGatewayAdapter`, never on Razorpay
  → **Dependency Inversion Principle**.
- Adding PayPal = one new file, zero edits to existing files → **Open/Closed Principle**.
- In tests you pass a `FakeAdapter` that always returns `True`. No network.

---

## Layer 5 — `controller/` : the door

```python
class EntryController:
    def enter_vehicle(self, license_plate, vehicle_type) -> EntryResult:
        slot = self._slot_service.allocate_slot(vehicle_type)
        if not slot:
            return EntryResult(False, None, None, f"No available slots for {vehicle_type.value}")
        vehicle = Vehicle(license_plate, vehicle_type)
        ticket = self._ticket_service.generate_ticket(vehicle, slot.id)
        return EntryResult(True, ticket.id, slot.id, "Entry successful")
```

A controller does exactly four things:

1. accept primitives from the caller (a string plate, an enum)
2. call services **in order**
3. turn "no slot" into a *message*, not an exception
4. return a **result object**, never a raw domain object

```python
class EntryResult(NamedTuple):
    success: bool; ticket_id: Optional[str]; slot_id: Optional[str]; message: str
```

Why a result object instead of returning the `Ticket`? So the caller doesn't need to know
your internals, and so failure is *data* (`success=False, message=...`) rather than an
exception someone forgot to catch. In a web app this is literally your JSON response body.

`ExitController.exit_vehicle` is the same shape, just longer — the exit flow in seven
readable lines:

```python
ticket = get_ticket()            # guard: exists? active?
fee = pricing.calculate_fee(ticket)
if not payment.process_payment_with_retry(ticket_id, fee, 3):
    return ExitResult(False, None, fee, "Payment failed")
receipt = receipt_service.generate_receipt(ticket, fee)
receipt_service.mark_receipt_as_paid(receipt)
slot_service.release_slot(ticket.slot_id)
ticket_service.deactivate_ticket(ticket_id)
return ExitResult(True, receipt.id, fee, "Exit successful")
```

**Notice the ordering: take money first, free the slot second.** If payment fails you return
early and the slot stays occupied — the car hasn't left. That ordering *is* the design. If an
interviewer asks one deep question about your exit flow, it will be this one.

---

## Layer 0 — `main.py` : wiring

```python
floor_repo = FloorRepository(); slot_repo = SlotRepository(); ...
admin_service = AdminService(floor_repo, slot_repo, pricing_repo)
entry_controller = EntryController(ticket_service, slot_service)
```

Nothing constructs its own dependencies — everything is handed in through the constructor.
That's **Dependency Injection**, and `main` is the one place allowed to know the concrete
types. In Spring or Django a framework does this for you; in an interview you do it by hand
in `main` and say "in production a DI container wires this."

---

## The two flows, end to end

**Entry**

```
main -> EntryController.enter_vehicle("ABC-123", CAR)
     -> SlotService.allocate_slot(CAR)
          -> SlotRepository: first free CAR slot, mark occupied
     -> new Vehicle("ABC-123", CAR)
     -> TicketService.generate_ticket(vehicle, slot.id)
          -> new Ticket(entry_time=now) -> save
     <- EntryResult(success=True, ticket_id=..., slot_id=...)
```

**Exit**

```
main -> ExitController.exit_vehicle(ticket_id)
     -> TicketService.get_ticket             (guard: exists? active?)
     -> PricingService.calculate_fee         (now - entry_time, rule lookup, min(flat, hourly))
     -> PaymentService.process_payment_with_retry(3)
          -> Razorpay -> fail -> Stripe -> success
     -> ReceiptService.generate_receipt + mark_as_paid
     -> SlotService.release_slot(ticket.slot_id)      (occupied = False)
     -> TicketService.deactivate_ticket               (active = False)
     <- ExitResult(success=True, receipt_id=..., fee=...)
```

**If you can draw those two ladders on a whiteboard from memory, you understand this design.**
Everything else — which file, which folder — is muscle memory, and `02-build-order.md` is
how you build it.
