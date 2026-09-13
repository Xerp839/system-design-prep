# 02 — Build Order: the plan → write → plan → write recipe

This is the file you actually asked for. Your instinct is correct: **nobody designs the whole
thing and then types it out.** You make several passes over the problem, each pass adding one
layer of detail, and you write code as soon as a pass gives you something concrete.

But I want to sharpen your mental model in one place, because it's the thing that trips up
most people at your stage.

---

## The one correction to your plan

You said:

> write down the entities first, then write the domain folder with only `__init__`,
> then plan the flow and list all the methods.

That's right for the **domain layer only**. After that, stop thinking in *layers* and start
thinking in *flows*.

**Do not** write all 5 repositories, then all 6 services, then all 3 controllers. That is
"horizontal" building, and it has two fatal problems in an interview:

- You have nothing runnable until the very last minute. If you run out of time at 35 minutes
  you have a pile of classes and zero working features.
- You write methods you turn out not to need, because you guessed at them before the flow
  told you what it wanted.

**Do this instead — "vertical slices":**

```
HORIZONTAL (bad)                     VERTICAL (good)
                                    
domain   ████████████               domain   ████████████    <- one horizontal pass, it's cheap
repo     ████████████               repo     ██  ██  ████
service  ████████████               service  ██  ██  ████
ctrl     ████████████               ctrl     ██    ██
         ^ nothing works                     ENTRY EXIT
           until the end                     ^each column runs on its own
```

Domain is the exception — it's 7 tiny classes, it anchors all your vocabulary, and it's fast.
Do it in one pass. Everything above domain, you build **one flow at a time, top to bottom,
and you run it before starting the next flow.**

Order of flows: **Entry → Exit.** Entry is the smallest complete story; exit has the
interesting logic. There is no third flow — see Pass 7 on why admin is something you
*describe*, never type.

**The budget:** a realistic 45-minute answer is ~400 lines. `Parking Lot Design/` is 421.
If your plan implies much more than that, cut scope now, not at minute 40.

---

## The 7 passes

### PASS 1 — Requirements (PLAN, ~4 min, no code)

Out loud, and on the board in bullet form. You are converting a vague prompt into a
**closed list of verbs**.

Ask these, and actually wait for answers:

- Multiple floors? Multiple lots? *(assume: multiple floors, one lot)*
- Which vehicle types? *(bike / car / truck / EV)*
- Pricing: flat, hourly, or both? *(both — hourly with a flat-rate cap)*
- Is payment in scope? Real gateway or stubbed? *(stubbed behind an interface)*
- Reservations / monthly passes / license-plate recognition? *(assume out of scope)*
- Do I need real concurrency or is single-threaded fine? *(say: "I'll design for it, mention locking, not implement threads")*

Then write the scope box on the board and **freeze it**:

```
IN:   entry -> assign slot, issue ticket
      exit  -> compute fee, take payment, receipt, free slot
OUT:  reservations, passes, ANPR, multi-lot, auth
      admin CRUD (seeded in main; I'll describe it, not build it)
```

> This box is your defence for the rest of the hour. When you're at minute 40 and the
> interviewer asks about monthly passes, you point at OUT and say "I scoped that out —
> want me to spend the last 5 minutes on it?"

### PASS 2 — Nouns (PLAN, ~3 min, no code)

Read your requirements back and **circle every noun**. That's your domain layer. Literally
that mechanical.

> "A **vehicle** arrives, gets a **slot** on a **floor**, receives a **ticket**. At exit a
> **pricing rule** gives a fee, a **payment** is taken, a **receipt** is issued."

```
Vehicle  ParkingSlot  Floor  Ticket  PricingRule  Payment  Receipt
```

For each, write attributes only — **no methods yet**:

```
Vehicle      licensePlate, vehicleType(enum)        <- plate is the identity
ParkingSlot  id, slotType(enum), occupied(bool), floorNumber
Floor        floorNumber, slots[]                   <- owns its slots
Ticket       id, licensePlate, vehicleType, slotId, entryTime, active(bool)
PricingRule  vehicleType, ratePerHour, flatRate
Payment      id, ticketId, amount, gateway(enum), status(enum)
Receipt      id, ticketId, exitTime, totalFee, paymentStatus(enum)
```

Three rules I want you to apply here every single time:

1. **Every type-ish field becomes an enum.** `vehicleType`, `status`, `gateway`.
2. **Don't invent an id when a natural key exists.** A license plate is already unique —
   giving `Vehicle` a UUID beside it means maintaining two identities for one car.
3. **Every "points at another thing" field becomes an `id`, not an object** — it keeps the
   object graph flat and matches a DB row. **But the moment you do this, ask "will I need to
   look that thing up later?"** If yes, you owe yourself either a repository to resolve it or
   a copy of the field you need.

Rule 3 is where the original version broke: `Ticket` held a `vehicleId`, no `VehicleRepository`
existed, so `PricingService` gave up and hardcoded `CAR` — every bike billed at car rates.
The fix here is the *copy* branch: `Ticket` carries `vehicleType` directly, which is also
more correct, because a ticket should record what was agreed at entry and not change if the
vehicle record is edited later.

### PASS 3 — Domain (WRITE, ~6 min)

Now type. `__init__` plus enums plus `__str__`. That's it.

```python
# domain/vehicle.py
class VehicleType(Enum):                     # module level, not nested
    BIKE = "BIKE"; CAR = "CAR"; TRUCK = "TRUCK"; EV = "EV"

class Vehicle:
    def __init__(self, license_plate, vehicle_type):
        self.license_plate = license_plate   # the plate IS the identity — no uuid
        self.vehicle_type = vehicle_type
```

Use readable ids where you do need one — `itertools.count` giving `T-1`, `S-F0-011`, `R-1`.
Your demo output has to be legible to the person watching you.

Add a domain method **only when it's a one-liner about the object's own state**:
`ticket.deactivate()`, `payment.mark_as_success()`, `floor.add_slot(s)`.
If it needs to look at another object, it is not a domain method — it's a service method.
That single sentence is your whole test.

Say out loud while typing: *"I'm keeping these anemic on purpose — behaviour that spans
entities goes into services."*

### PASS 4 — The flow ladder (PLAN, ~4 min, no code)

**This is the pass people skip, and it's the one that makes the writing easy.**

For each flow, write the numbered ladder on the board. Pure English, no syntax:

```
ENTRY(plate, type):
  1. find a free slot of that type       -> who owns this? SlotService
  2. mark it occupied                    -> SlotService
  3. create the vehicle                  -> (just construct it)
  4. create a ticket (vehicle, slot, now)-> TicketService
  5. return {ticketId, slotId}

EXIT(ticketId):
  1. load the ticket; error if missing / inactive   -> TicketService
  2. fee = f(entryTime, now, pricing rule)          -> PricingService
  3. take payment, retry on failure                 -> PaymentService
  4. make receipt                                   -> ReceiptService
  5. free the slot                                  -> SlotService
  6. deactivate the ticket                          -> TicketService
  7. return {receiptId, fee}
```

Now the magic: **the right-hand column IS your service layer.** You didn't invent
`SlotService` / `TicketService` / `PricingService` / `PaymentService` / `ReceiptService` by
guessing — the flow named them. Each step's verb became a service method.

While you have the ladder up, do two more things:

- **Argue the ordering.** Why is "take payment" step 3 and "free the slot" step 5? Because if
  payment fails the car is still there. Say this. It's the highest-value sentence in the hour.
- **Derive the repositories.** Anything the ladder says "load" or "save" about needs storage:
  ticket, slot, floor, pricing rule, payment. Five repositories. Again — derived, not guessed.

Write the method list before you write the methods:

```
TicketService   generate_ticket(vehicle, slot_id) -> Ticket
                get_ticket(id) -> Ticket | None
                close_ticket(ticket)
SlotService     allocate_slot(type) -> Slot | None      # policy lives here
                release_slot(slot_id)
                availability(type) -> {floor: count}
PricingService  calculate_fee(ticket, now=None) -> float
PaymentService  process_payment(ticket_id, amount, max_attempts=3) -> bool
ReceiptService  issue_receipt(ticket, fee) -> Receipt
```

Every signature comes straight off the ladder. **You now have nothing left to think about
while typing** — which is the entire point of the plan/write rhythm.

### PASS 5 — Vertical slice 1: ENTRY (WRITE, ~8 min)

Write *only* what the entry ladder needs, bottom to top:

1. `FloorRepository` — `save`, `find_all`, `find_slot` (the id → slot index)
2. `TicketRepository` — `save`, `find_by_id`
3. `SlotService.allocate_slot` (walks floors, picks, calls `slot.occupy()`),
   `TicketService.generate_ticket`
4. `EntryResult` + `EntryController.enter_vehicle`
5. A tiny `main` that wires two repos, two services and one controller, seeds one floor
   with a few slots, and parks a car.

**Run it.** Print the ticket id and the per-floor availability before and after. You now
have a working, *visible* feature at minute ~25.

Do NOT write payments yet. Do NOT write receipts yet. Resist.

### PASS 6 — Vertical slice 2: EXIT (WRITE, ~10 min)

Now the same thing for exit:

1. `PricingRuleRepository`, `PaymentRepository`, `ReceiptRepository`
2. `PaymentGatewayAdapter` (ABC) + one fake implementation returning `True`
3. `PricingService.calculate_fee`, `PaymentService.process_payment`,
   `ReceiptService.issue_receipt`
4. `ExitResult` + `ExitController.exit_vehicle`
5. Extend `main`: park a car, exit it, print the fee.

**Run it again.** At minute ~40 you have both core flows working end to end.

### PASS 7 — Talk, don't type (remaining time)

**Do not write an admin layer.** This is the single biggest time trap in this problem.

The version you're learning from originally had one — `AdminService` + `AdminController` +
an extra repository, **108 lines** — and all it did was create three floors and set four
prices. In `main.py` that is now a dict and a loop:

```python
LAYOUT = {0: [(VehicleType.BIKE, 10), (VehicleType.CAR, 15), (VehicleType.TRUCK, 3)],
          1: [(VehicleType.CAR, 20), (VehicleType.EV, 5)]}
```

Admin is CRUD. CRUD demonstrates nothing about your design ability, and 108 lines is a
quarter of your time budget. Say this instead:

> *"Admin is CRUD over the floor and pricing repositories — add floor, add slots, update a
> rule. I've seeded it in `main` instead so I can spend the time on how I'd handle two gates
> racing for the last slot. Shall I?"*

That reads as senior: you named the work, judged its value, and offered something better.
Silently running out of time does not.

Spend the remaining minutes on whichever of these they bite on — each is in the curveball
list at the end of this file:

- concurrency on slot allocation (your strongest card)
- pricing as a Strategy when rules multiply
- slot-type compatibility (a car in a truck slot)
- O(1) slot lookup at 10,000 slots

---

## The rhythm, compressed

| # | Mode | Output | Minutes |
| :- | :- | :- | :- |
| 1 | PLAN | frozen scope box (IN / OUT) | 4 |
| 2 | PLAN | noun list + attributes + enums | 3 |
| 3 | WRITE | `domain/` — `__init__` only | 6 |
| 4 | PLAN | numbered flow ladders → services + repos + signatures | 4 |
| 5 | WRITE | ENTRY slice, repo→service→controller→main, **run it** | 8 |
| 6 | WRITE | EXIT slice, **run it** | 10 |
| 7 | TALK | admin (describe, don't type), concurrency, extensions | rest |

Two rules that hold the whole thing together:

- **Never write a class you haven't named in a plan pass.** If you find yourself inventing
  a class mid-typing, stop, go back to the board, put it in the ladder, then type it.
- **Never plan more than ~4 minutes without producing code.** If a plan pass is running
  long, your scope is too big — cut something into the OUT box.

---

## Where each kind of code goes (the decision table)

When you're mid-flow and unsure where a line belongs, this table answers it:

| The line... | goes in |
| :--- | :--- |
| stores or retrieves objects; dict/SQL access | **repository** |
| touches only one entity's own fields | **domain** (as a method on that entity) |
| coordinates 2+ entities or repositories; implements a rule | **service** |
| decides call order for a use case, builds the response | **controller** |
| speaks someone else's API | **adapter** |
| constructs concrete classes | **main** only |

And the smells that tell you you got it wrong:

- A controller doing arithmetic → that rule belongs in a service.
- A service opening a dict directly → you skipped a repository.
- A domain class importing a repository → your layers are inverted, fix it now.
- A service importing a concrete `RazorpayAdapter` → should depend on the ABC and be injected.

---

## What to do when the interviewer changes the requirements

They will. This is the real test, and the layering is what makes you fast. Prepared answers:

**"Now a car can also park in a truck slot."**
> Only `SlotService.allocate_slot` changes. I'd replace the equality check with a
> compatibility map: `{BIKE: [BIKE], CAR: [CAR, TRUCK], TRUCK: [TRUCK], EV: [EV, CAR]}`,
> and prefer the tightest fit first so I don't burn a truck slot on a hatchback.
> Nothing else in the system moves.

**"Add weekend pricing / first 30 minutes free."**
> That's `PricingService` only. This is where I'd introduce the **Strategy pattern** — a
> `PricingStrategy` interface with `HourlyStrategy`, `FlatStrategy`, `WeekendStrategy`,
> picked per vehicle type. Open/Closed: new pricing is a new class, not an edited method.
> *(You already have Strategy in `3.Strategy Design Pattern/` — this is the same shape.)*

**"Two gates, same last slot, at the same instant."**
> Today `allocate_slot` is read-then-write, so both cars could win. I'd make it atomic:
> a per-lot lock, or in a real DB a single conditional update
> `UPDATE slots SET occupied=true WHERE id=? AND occupied=false` and check rows-affected.
> Availability *counts* can stay eventually-consistent; the *assignment* must not be.

**"Add PayPal."**
> One new file implementing `PaymentGatewayAdapter`. Zero edits to existing files.
> That's the whole reason the adapter exists.

**"Driver lost the ticket."**
> Look up the active ticket by license plate (I'd add `find_active_by_vehicle` on
> `TicketRepository` plus a `VehicleRepository` index on plate), charge a lost-ticket
> penalty plus max daily rate, and require admin override to authorise it.

**"How would you find a free slot fast with 10,000 slots?"**
> The linear scan in `allocate_slot` is O(n). I'd keep a per-(floor, type) queue or heap of
> free slot ids — O(1) pop on entry, O(1) push on release. If I want "nearest to the exit,"
> a min-heap keyed by distance. I'd mention this and note I kept the scan for clarity.

Having four or five of these ready is worth more than writing perfect code, because this is
where the interviewer actually decides whether you designed it or memorised it.
