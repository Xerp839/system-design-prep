# 04 — What's Broken in the Copied Code

I ran `Parking Lot Design/main/main.py`. **It does not execute.** First failure:

```
ImportError: attempted relative import beyond top-level package
```

That's not a criticism of you — you copied it, and the original was Java. But fixing this
is the single best exercise available to you right now, because every bug is a *specific*
lesson. Work top to bottom; don't read my fix until you've tried.

---

## Part A — Bugs that stop it running (fix these first)

### A1. Relative imports vs. how you run it — `main/main.py`

Every module uses package-relative imports (`from ..domain.floor import Floor`), but
`main.py` does `sys.path.append(...)` and then uses absolute ones (`from domain.floor import Floor`).
Those two styles can't coexist, and `Parking Lot Design` has a space in its name so it isn't
an importable package name anyway.

**Fix:** rename the directory to `parking_lot` (no space), delete the `sys.path` hack, put
`main.py` at the package root next to `domain/`, make all imports relative (`from .domain...`),
and run it from `system-design-prep/` with:

```
python -m parking_lot.main
```

*Lesson: decide "is this a package or a script folder" before you write the first import.*

### A2. `reciept.py` vs `receipt.py` — file name typo

- `domain/reciept.py` defines `Receipt`
- `service/reciept_service.py` does `from ..domain.receipt import Receipt` → no such module
- `controller/exit_controller.py` does `from ..service.receipt_service import ReceiptService` → no such module
- `main.py` does `from service.receipt_service import ReceiptService` → no such module

**Fix:** rename both files to `receipt.py` and `receipt_service.py`.

### A3. `TicketService.deactivate_ticket` calls a method that doesn't exist

```python
def deactivate_ticket(self, ticket_id: str):
    self._ticket_repository.de_activate_ticket(ticket_id)  # AttributeError
    # ... two confused comments ...
    self._ticket_repository.deactivate_ticket(ticket_id)
```

The author was mid-thought about Java naming and left both lines in. The first one raises.

**Fix:** delete the first call and both comments. One line survives.

### A4. `main.py` imports a class that doesn't exist

```python
from service.payment_service import Payment_Service # Re-checking class name
from service.payment_service import PaymentService
```

**Fix:** delete the first line.

### A5. `ReceiptService` import path

`service/reciept_service.py` imports `..domain.receipt` — fixed by A2, but check it after
renaming.

> After A1–A5, it runs. **Do that much before reading Part B.**

---

## Part B — Real design bugs (these are the interesting ones)

### B1. `PricingService` hardcodes CAR — every vehicle is billed as a car

```python
def calculate_fee(self, ticket):
    vehicle_type = Vehicle.VehicleType.CAR  # Default demo type
```

A bike parked for an hour is billed at the car rate. This is *the* design flaw, and it's a
symptom of something structural: `Ticket` stores `vehicle_id`, but **there is no
`VehicleRepository`**, so there is genuinely no way to resolve that id back to a vehicle.
The `Vehicle` object created in `EntryController` is constructed, used for its `id`, and
then thrown away — it is never persisted anywhere.

Two legitimate fixes, and **you should be able to argue for both**:

**Fix 1 — add the missing repository (the "normalised" answer).**
Create `VehicleRepository`, save the vehicle in the entry flow, then:
```python
vehicle = self._vehicle_repository.find_by_id(ticket.vehicle_id)
rule = self._pricing_rule_repository.find_by_vehicle_type(vehicle.vehicle_type)
```
Correct, and you now have a place to index by license plate — which you need for the
lost-ticket case anyway.

**Fix 2 — denormalise onto the ticket (the "pragmatic" answer).**
Add `vehicle_type` to `Ticket` at creation. One field, no extra lookup, and it's arguably
*more* correct: the ticket should record what was actually billed at entry time, frozen,
even if the vehicle record is edited later.

*Lesson: when you replace an object reference with an id, you owe yourself either a
repository to resolve it or a denormalised copy of the field you need. Pick one, deliberately.*

### B2. `PaymentService` permanently switches to Stripe and never switches back

```python
def process_payment_with_retry(self, ticket_id, amount, max_retries):
    for i in range(1, max_retries + 1):
        if self.process_payment(ticket_id, amount): return True
        if i == 1:
            self._default_gateway = StripeAdapter()   # mutates the SERVICE
```

`_default_gateway` is instance state on a long-lived service. One customer's failed payment
permanently flips the gateway for **every future customer**. There's a second bug stacked on
it: `process_payment` always records `Payment.PaymentGateway.RAZORPAY` on the Payment row,
so after the switch your audit trail lies about which gateway was used.

**Fix:** make the gateway a local variable, and pass it down:

```python
def __init__(self, payment_repository, gateways=None):
    self._payment_repository = payment_repository
    self._gateways = gateways or [
        (Payment.PaymentGateway.RAZORPAY, RazorpayAdapter()),
        (Payment.PaymentGateway.STRIPE,   StripeAdapter()),
    ]

def process_payment_with_retry(self, ticket_id, amount, max_retries):
    for attempt in range(max_retries):
        gateway_enum, adapter = self._gateways[min(attempt, len(self._gateways) - 1)]
        if self._process_once(ticket_id, amount, gateway_enum, adapter):
            return True
    return False
```

*Lesson: mutable state on a shared service is how one request poisons the next. Prefer
locals, or pass the choice in.*

### B3. The slot leaks if anything after allocation fails

```python
slot = self._slot_service.allocate_slot(vehicle_type)   # slot is now occupied=True
vehicle = Vehicle(license_plate, vehicle_type)
ticket = self._ticket_service.generate_ticket(vehicle, slot.id)   # if this throws...
```

If ticket creation fails, the slot stays occupied forever and no ticket exists to release it.

**Fix:** wrap in try/except and release the slot on failure — a compensating action. In a
real system: one database transaction.

*Lesson: any time you mutate shared state and then do more work, ask "what if the rest fails?"*

### B4. Slot allocation is not atomic

```python
for slot in self._slots.values():
    if slot.slot_type == vehicle_type and not slot.occupied:
        slot.occupied = True
```

Read-then-write. Two gates, two threads, one free slot, both cars get it.

**Fix (in-memory):** a `threading.Lock` around allocate/release.
**Fix (real DB):** `UPDATE slots SET occupied=true WHERE id=? AND occupied=false` and check
rows-affected — let the database do the compare-and-swap.

*This is the #1 follow-up question in a parking-lot interview. Raise it before they do.*

### B5. Receipt is marked paid, but never saved

```python
receipt = self._receipt_service.generate_receipt(ticket, fee)
self._receipt_service.mark_receipt_as_paid(receipt)
```

There is no `ReceiptRepository`. The receipt object exists for the length of the function
and is garbage-collected. `ExitResult` returns a `receipt_id` that can never be looked up.

**Fix:** add `ReceiptRepository` and save it.

### B6. `generate_receipt_text` silently creates a *second* receipt

```python
def generate_receipt_text(self, ticket_id):
    fee = self._pricing_service.calculate_fee(ticket)   # recomputed — later time, LARGER fee
    receipt = self._receipt_service.generate_receipt(ticket, fee)  # a brand new receipt!
```

`main.py` calls this right after `exit_vehicle`, so the printed receipt has a **different id,
a different exit time, and possibly a different fee** than the one that was actually paid.

**Fix:** once B5 exists, look the receipt up by id instead of regenerating it. Never
recompute a price you've already charged.

### B7. Fee arithmetic: `//` truncates, and money is a float

```python
hours = max(1, duration.total_seconds() // 3600)
```

61 minutes bills as 1 hour. Real lots round *up*. And `float` for currency accumulates
rounding error.

**Fix:** `hours = max(1, math.ceil(duration.total_seconds() / 3600))`, and store money as
integer paise or `Decimal`.

### B8. Slot type is rigid — a car can't use a truck slot

`slot_type == vehicle_type` exactly. Real lots allow a small vehicle in a larger slot.
See the compatibility-map answer in `02-build-order.md`.

### B9. `get_slot_statistics` counts *total* slots, not free ones

```python
def get_slot_statistics(self):
    stats = {}
    for slot in self._slots.values():
        stats[slot.slot_type.value] = stats.get(slot.slot_type.value, 0) + 1
```

No `occupied` check, so "parking status" — the one thing an admin actually wants — always
reports the same numbers. Should report free and total per type.

### B10. `ParkingSlot.occupied` is public and mutated from three places

`SlotRepository.allocate_slot`, `SlotRepository.release_slot`, and anything else that feels
like it. There's no single owner of that transition.

**Fix:** put `occupy()` / `release()` on `ParkingSlot`, have them raise if already in that
state, and make everyone go through them. That's encapsulation doing real work — it turns
a silent double-release into a loud error.

### B11. `AdminService._add_floor` / `add_floor_public`

Java private/public transliterated. In Python, one public `add_floor` is enough. Cosmetic,
but interviewers read it as "ported without understanding."

---

## Your exercise

1. Fix A1–A5. Get it running. (~20 minutes)
2. Fix B1, B2, B5, B6. (~40 minutes) — these four are the ones an interviewer would find.
3. Fix B4 with a lock, and write a comment explaining the DB equivalent.
4. Then delete the whole folder and rebuild it from `02-build-order.md` without looking.

Step 4 is the one that matters. The first three are just how you earn the right to do it.
