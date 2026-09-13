# 03 — Interview Playbook

`02-build-order.md` is the method. This is the same thing as a clock, plus the sentences
to say. LLD rounds are usually 45–60 minutes. Assume 45 and finish early.

---

## The clock

| Minute | You are doing | Visible output |
| :--- | :--- | :--- |
| 0–4 | Clarifying questions, freeze scope | IN/OUT box on the board |
| 4–7 | Name the nouns + attributes | entity list |
| 7–13 | Type `domain/` | 7 small classes |
| 13–17 | Flow ladders → derive services + repos | numbered steps + signatures |
| 17–25 | ENTRY slice, bottom to top | **running code** |
| 25–35 | EXIT slice | **running code** |
| 35–40 | Admin (or say you'd skip it) | CRUD, or a sentence |
| 40–45 | Edge cases, concurrency, extensions | discussion |

If you're behind at minute 25 with no running entry flow, **cut admin and cut the receipt
text formatting** and say so. Delivering two working flows beats five half-flows every time.

---

## Sentences to have ready

**Opening (after they state the problem):**
> "Let me restate it and then ask a few scoping questions before I write anything."

**Freezing scope:**
> "I'm putting reservations, monthly passes and plate recognition out of scope so I can get
> entry and exit fully working. If there's time I'll come back to them — does that work?"

**Before typing domain:**
> "I'll keep these entities mostly data — anything that spans two entities I'll put in a
> service, so the business rules live in one layer."

**Introducing the layering (do this once, early, and briefly):**
> "I'll use controller → service → repository → domain. Controllers decide the order of
> operations, services hold the rules, repositories hide storage — in-memory dicts today,
> a database later, and nothing above them would change."

**When a service looks trivially thin:**
> "This is a pass-through today. It exists because validation, the QR code, and the entry
> SMS all land here later, and I'd rather not move the seam then."

**The exit ordering (say this deliberately, don't rush it):**
> "Order matters here: I take payment before releasing the slot. If payment fails I return
> early and the slot stays occupied, because the car physically hasn't left."

**Naming your patterns — only where they earned their place:**
> "Three patterns: Adapter for the payment gateways so adding PayPal is a new file rather
> than an edit; Repository so the storage choice is a seam; and if pricing gets more rules
> I'd move it to Strategy."

**Admitting a shortcut (this scores, it doesn't cost):**
> "`allocate_slot` is a linear scan — O(n). With ten thousand slots I'd keep a free-list
> per floor and type for O(1). I kept the scan so the logic reads clearly."

**Closing:**
> "Both flows run. The things I'd do next, in order: make slot allocation atomic, move
> pricing to Strategy, and add the lost-ticket admin override."

---

## Red flags interviewers watch for

- Starting to code at minute 0. **Never.** Ask questions first, always.
- One `ParkingLot` god class with 20 methods.
- Storing money as `float`. (Mention it: *"I'd use integer paise/cents or `Decimal` in
  production — I'm using float here for speed."* The copied code uses float.)
- Patterns applied because you know their names. A Factory that makes one type of object
  is worse than no Factory. Only reach for one when a *changing requirement* motivates it.
- Silence. Narrate. A design round grades your reasoning, not your typing.
- Arguing with a requirement change instead of showing which file it touches.

## Green flags

- Deriving classes from the flow rather than from memory ("step 2 needs someone to own
  slot state — that's `SlotService`").
- Naming a trade-off before they find it.
- Running the code, even partially.
- Answering "what changes if X?" with "one file, here" — that's the payoff of layering
  and it's what they're really testing.

---

## The 60-second whiteboard picture

If you can only draw one thing, draw this:

```
              EntryController            ExitController            AdminController
                    |                          |                          |
        +-----------+                          |                    +-----+-----+
        |           |            +-------+-----+-----+-------+      |           |
   SlotService  TicketService   Pricing Payment  Receipt  Slot/Ticket        AdminService
        |           |             |       |                                     |
   SlotRepo    TicketRepo   PricingRuleRepo  PaymentRepo                  FloorRepo
        |           |             |       |                                     |
        +-----------+-------------+-------+-------------------------------------+
                                  |
                          domain: Vehicle, Floor, ParkingSlot,
                                  Ticket, PricingRule, Payment, Receipt

                          PaymentService ---> PaymentGatewayAdapter (ABC)
                                                 /            \
                                          Razorpay          Stripe
```

Then talk through the entry ladder and the exit ladder over the top of it.
