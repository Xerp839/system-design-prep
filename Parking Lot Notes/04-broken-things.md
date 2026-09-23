# 04 — What Was Broken, and What Changed

Two rounds of work happened to the code you copied:

1. **Round 1 — make it run.** It didn't execute at all (5 breakages from the Java port).
2. **Round 2 — make it interview-sized.** 597 lines was roughly 2x what you can hand-write
   in 45 minutes, and one of its abstractions was decorative.

Both are done. The original is preserved in git history on `main`; this branch
(`feat/refactor-parking-lot`) has the version you should learn from.

This file is the record of *why* each change was made. The reasoning transfers to every
other LLD problem — the specific bugs don't.

---

## Round 1 — five reasons it wouldn't run

### A1. Relative imports vs. how you run it

Every module used `from ..domain.floor import Floor`, but `main/main.py` did a
`sys.path.append(...)` and then used absolute imports. Those two styles can't coexist: `..`
means "go up one package," and when `main.py` is the entry point there is no package above
it — hence `ImportError: attempted relative import beyond top-level package`.

**Fixed by:** moving `main.py` to the folder root next to `domain/`, deleting the `sys.path`
hack, and rewriting all 41 `from ..x` imports as `from x`. Because `main.py` now sits at the
root, Python puts that directory on `sys.path` automatically and everything resolves with no
path manipulation. Single-dot imports *inside* a folder (`from .vehicle import VehicleType`)
were always fine and were left alone.

*Lesson: decide "importable package or script folder" before the first import — the two need
different syntax and different run commands.*

### A2. `reciept.py` vs `receipt.py`

`domain/reciept.py` defined `Receipt`, while two other files imported `domain/receipt.py`.
Renamed both it and `reciept_service.py`.

### A3. A call to a method that doesn't exist

```python
def deactivate_ticket(self, ticket_id):
    self._ticket_repository.de_activate_ticket(ticket_id)   # AttributeError
    # Actually Java had deactivateTicket, but I'll stick to correct naming in Python.
    # Wait, Java original had deactivateTicket.
    self._ticket_repository.deactivate_ticket(ticket_id)
```

Someone was mid-thought about Java naming and left both lines plus their thinking-out-loud in.

### A4. An import of a class that doesn't exist

```python
from service.payment_service import Payment_Service # Re-checking class name
```

Same story.

### A1b. Windows console encoding (not a port bug)

Once imports were fixed it still crashed: `UnicodeEncodeError` on the ✅ emoji, because
Windows consoles default to cp1252. Fixed with
`sys.stdout.reconfigure(encoding="utf-8")` in `main.py`.

---

## Round 2 — why it was too big, and what went

Measured before: **597 lines, 74 methods, 18 never called from outside their own file.**
After: **421 lines, 34 methods, effectively nothing unused.**

### The admin layer — deleted, 108 lines

`AdminService` + `AdminController` + a third repository existed to create three floors and
set four prices. In `main.py` that is now:

```python
LAYOUT = {0: [(VehicleType.BIKE, 10), (VehicleType.CAR, 15), (VehicleType.TRUCK, 3)],
          1: [(VehicleType.CAR, 20), (VehicleType.EV, 5)]}
```

Admin is CRUD. CRUD demonstrates nothing about design ability, and 108 lines is a quarter of
your time budget. In an interview you *describe* it. See Pass 7 in `02-build-order.md`.

### `Floor` was decorative — the worst problem

The measurement that found it: `floor.slots` was touched in exactly two places, both inside
`floor.py` itself. `AdminService` filled every floor with slots and **nothing ever read
them.** Allocation went through a separate `SlotRepository` holding its own flat dict of all
slots, scanning it floor-blind:

```python
for slot in self._slots.values():   # no floor awareness at all
```

Two containers holding the same objects, one of them write-only. Not a correctness bug — same
object references, so `occupied` flips were visible in both — but fatal for an interview. Ask
"how do you assign a slot near the entrance?" or "show availability per floor" and the `Floor`
class can't help. That reads as template-copied rather than designed.

**Fixed by deleting `SlotRepository` entirely.** Slots now live only inside their floor;
`FloorRepository` keeps an `id -> slot` **index** (same objects, not a copy) so release is
O(1). `SlotService` walks floors in order. `main.py` prints per-floor availability before and
after each entry, so you can *see* it working.

### Allocation policy moved out of the repository

`SlotRepository.allocate_slot()` found a free slot **and mutated it**. Which slot to hand out
is a *policy* decision, and policy in the storage layer is the wrong seam. It's now
`SlotService.allocate_slot`, where changing to nearest-to-exit or cheapest-floor touches one
method.

### Dead methods — deleted

`SlotService.create_slot`, `SlotService.get_available_slot_count`,
`TicketRepository.find_active_tickets`, `delete()` on three repositories, four
`AdminController` methods, `Floor.get_available_slots_count`. Speculative CRUD written
because "a repository should have those," not because anything needed them.

Every method you keep is a method you have to remember.

---

## Round 2 — the design bugs, and how each was fixed

### B1. Every vehicle was billed as a car

```python
vehicle_type = Vehicle.VehicleType.CAR  # Default demo type
```

A bike parked an hour was charged the car rate. This was a *symptom*: `Ticket` stored
`vehicle_id`, there was **no `VehicleRepository`**, and the `Vehicle` built in
`EntryController` was used for its id and thrown away. The code genuinely could not find out
what kind of vehicle it was.

**Fixed by denormalising:** `Ticket` now carries `vehicle_type` directly, and `Vehicle` lost
its UUID in favour of the license plate as natural key — so no `VehicleRepository` is needed
at all. This is also the *more correct* model: a ticket records what was agreed at entry, and
editing a vehicle record later must not change an in-flight charge.

> **The transferable rule:** when you replace an object reference with an id, you owe yourself
> either a repository to resolve it, or a copy of the field you need. Pick one deliberately.
> The bug is picking neither.

Guarded by `test_each_vehicle_type_is_priced_by_its_own_rule`.

### B2. One customer's failed card switched the gateway for everyone

```python
if i == 1:
    self._default_gateway = StripeAdapter()   # mutates the SERVICE
```

`_default_gateway` was instance state on a long-lived service, so it never went back to
Razorpay. Worse, `process_payment` always recorded `RAZORPAY` on the `Payment` row, so after
the switch the audit trail lied.

I proved it before fixing — forcing Razorpay to fail left the service on
`gateway now: StripeAdapter` permanently.

**Fixed by** injecting a `[(enum, adapter)]` list and choosing per attempt as a **local**:

```python
gateway, adapter = self._gateways[min(attempt, len(self._gateways) - 1)]
payment = self._payment_repository.save(Payment(ticket_id, amount, gateway))
```

Each row now records the gateway actually used. Guarded by
`test_payment_falls_back_to_the_second_gateway`, which asserts both the statuses and the
gateways in order.

*Lesson: mutable state on a shared service is how one request poisons the next.*

### B3. The slot leaked if anything after allocation failed

The slot was occupied before the ticket was created; if that threw, nothing could ever free
it. **Fixed** with a compensating action in `EntryController`:

```python
except Exception:
    self._slot_service.release_slot(slot.id)
    raise
```

*Lesson: every time you mutate shared state, ask "what if the next line fails?"*

### B4. Slot allocation was not atomic

Read-then-write: two gates, one free slot, both cars win. **Fixed** with a `threading.Lock`
in `SlotService`, plus a comment naming the real answer:

```python
# In a real DB this becomes UPDATE ... WHERE id=? AND occupied=false
```

**This is the #1 follow-up question in a parking-lot interview.** Raise it before they do.

### B5 + B6. The receipt was never saved, and printing it made a second one

`generate_receipt_text` recomputed the fee (at a later time, so possibly *larger*) and built
a brand-new `Receipt`. `main.py` called it right after `exit_vehicle`, so the printed receipt
had a different id, a different exit time, and a `PENDING` status — for a payment that had
already succeeded. That wrong output was visible on screen once the code ran.

**Fixed by** deleting `generate_receipt_text` (15 lines of string formatting, zero design
content), adding a `ReceiptRepository`, and making `Receipt` **born `SUCCESS`** — it is only
ever created after a payment succeeds, so there's no `mark_as_paid()` step to forget.

*Lesson: never recompute a price you have already charged. And where it's cheap, make illegal
states unrepresentable instead of relying on someone calling a setter.*

### B7. Fee arithmetic

`duration.total_seconds() // 3600` truncates — 61 minutes billed as one hour. **Fixed** to
`math.ceil(...)`, which is what real car parks do.

Money is still `float`. That's a deliberate, stated shortcut: `Decimal` arithmetic adds noise
to a file meant for learning. Say "integer paise or `Decimal` in production" in the interview
and it costs you nothing.

`calculate_fee` also gained an injectable `now` parameter, which makes it pure and lets
`test_flat_rate_caps_a_long_stay` price a ten-hour stay instantly. That's also your answer to
the "system clock mismatch" edge case.

### B10. Slot state had no owner

`occupied` was public and flipped from several places. **Fixed** with guarded transitions:

```python
def occupy(self):
    if self.occupied:
        raise ValueError(f"Slot {self.id} is already occupied")
    self.occupied = True
```

A double-book is now a loud error instead of a silent overwrite. Guarded by
`test_a_slot_cannot_be_double_booked`.

### Also fixed, briefly

- **Duplicate `PaymentStatus`** — was declared in both `payment.py` and `receipt.py` as two
  unrelated enums that could drift. Now declared once and imported.
- **Nested enums** (`Vehicle.VehicleType`) → module-level `VehicleType`, the Python idiom.
- **UUIDs** → `itertools.count` ids (`T-1`, `S-F0-011`, `R-1`), so demo output is legible.
- **`_add_floor` / `add_floor_public`** pairs — Java access modifiers transliterated. Gone
  with the admin layer.

---

## Still open, on purpose

Two things I did **not** fix, because they're better as talking points than as code:

- **B8 — slot compatibility.** A car still can't use a truck slot. The fix is a compatibility
  map in `SlotService.allocate_slot`, preferring the tightest fit. It's in the curveball list
  in `02-build-order.md`.
- **Pricing as Strategy.** Justified only once rules multiply (weekends, free first 30
  minutes). Adding it now would be a pattern applied for its own sake — which is itself a red
  flag. Say "if pricing grows, I'd move it to Strategy" instead.

---

## Your exercise

The repair work is done, so the exercise is now the one that actually matters:

1. Read `git diff main..feat/refactor-parking-lot -- "Parking Lot Design"` and make sure you
   can explain **why** for each change, not just what.
2. Then delete the folder and rebuild it from `02-build-order.md` without looking.

Step 2 is the point. Step 1 is how you earn the right to do it.
