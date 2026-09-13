# 05 — Practice Drill

Goal: **write this from a blank folder, unaided, in 45 minutes.** Reading the design does
not get you there. These reps do. Spread them over ~2 weeks, one rep per sitting.

---

## Rep 0 — Repair (1–2 sittings)

Work through `04-broken-things.md`. Get `main.py` running, then fix B1, B2, B5, B6.
You're not writing new design here, you're reading someone else's closely — which is a
different and useful skill.

## Rep 1 — Ladders from memory (15 min, no code)

Blank paper. Write:

- the 7 domain entities and their attributes
- the entry ladder (5 steps) with the owning service beside each step
- the exit ladder (7 steps) with the owning service beside each step

Check against `01-code-walkthrough.md`. If you missed a step, redo the whole ladder rather
than patching it — you want the sequence to feel like one unit, not seven facts.

**Repeat this rep until it's boring.** It's 15 minutes and it's 70% of the value.

## Rep 2 — Domain layer, blind (20 min, code)

New folder. Write `domain/` only, from memory. No looking.
Then diff against the original. You are checking two things:
did you enum everything, and did you keep methods to single-entity one-liners.

## Rep 3 — Entry slice, blind (30 min, code)

Same folder. `SlotRepository` → `TicketRepository` → `SlotService` → `TicketService` →
`EntryController` → `main`. Hand-create three slots in `main`. **Run it.**

Success = a printed ticket id.

## Rep 4 — Exit slice, blind (40 min, code)

Add pricing, payment (with the adapter ABC and one fake gateway), receipt, `ExitController`.
**Run it.** Success = a printed fee that changes if you fake an older `entry_time`.

## Rep 5 — Full run, timed (45 min, strict clock)

Empty folder. Timer on. Follow the 7 passes in `02-build-order.md`, including the plan
passes on paper. Stop dead at 45 minutes whatever state you're in.

Then score yourself honestly:

- [ ] Did I ask clarifying questions before typing? (even alone — say them out loud)
- [ ] Did I write the ladders before the services?
- [ ] Did entry run before I started exit?
- [ ] Did I talk through the payment-before-release ordering?
- [ ] Did I name my trade-offs unprompted?
- [ ] Did I finish with both flows executing?

Whichever box is unticked is the one thing to fix in the next rep. Don't fix everything at once.

## Rep 6 — Curveballs (20 min, talking only)

Set a timer for 3 minutes per question. Answer out loud, naming the exact files that change:

1. Cars may park in truck slots.
2. First 30 minutes free; weekends 2x.
3. Monthly pass holders park free.
4. Two entry gates, one free slot, same instant.
5. Add PayPal.
6. Driver lost the ticket.
7. 10,000 slots — find a free one in O(1).
8. Show live availability per floor on a display board at the entrance.
9. EV slots have chargers and bill for electricity separately.
10. The lot has multiple physical locations.

Model answers for 1, 2, 4, 5, 6, 7 are at the bottom of `02-build-order.md`.
Numbers 3, 8, 9 and 10 are yours to work out — that's the point.

Hint for 8: this is the **Observer pattern**, which you already built in
`5.Observer Desgin Pattern/`. `SlotService` publishes a slot-state-changed event; the display
board subscribes. Notice how the folder you already have is the answer — that's how the
pattern folders are supposed to pay off.

---

## Reusing this method on the next problem

The 7 passes are not parking-lot-specific. Every LLD problem is the same shape:

| Pass | Parking Lot | Elevator | Splitwise | BookMyShow |
| :- | :- | :- | :- | :- |
| nouns | Slot, Ticket, Floor | Elevator, Request, Floor | User, Group, Expense, Split | Show, Seat, Booking, Screen |
| the flows | entry / exit | request / dispatch / move | add expense / settle up | search / hold seat / pay |
| the interesting rule | fee calculation | which lift to send | how to split | seat hold + expiry |
| the Strategy slot | pricing | dispatch algorithm | split type (equal/exact/%) | pricing tier |
| the Adapter slot | payment gateway | hardware controller | payment gateway | payment gateway |
| the concurrency question | two gates, one slot | two calls, one lift | concurrent settlements | two users, one seat |

Notice the last three rows repeat almost verbatim. **Once you can do parking lot cold, you
have most of Splitwise and BookMyShow already.** Do parking lot properly rather than doing
three problems badly.

Suggested order after this: **Splitwise** (different domain, similar shape, exercises
Strategy hard) → **Elevator** (introduces state machines and scheduling) → **BookMyShow**
(introduces holds, expiry and real concurrency pressure).
