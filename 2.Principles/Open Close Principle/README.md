# Open/Closed Principle (OCP)

## What it means

**Open for extension, closed for modification.**

You should be able to add new behavior **without editing existing, working code**. Extend via new classes — don't keep patching the same class with `if/elif` chains.

---

## Our example: Payment processing

We process payments through different methods (UPI, credit card, net banking, etc.).

---

## Bad example — `bad_example.py`

**Problem:** `PaymentProcessor.pay()` uses a big `if/elif` on `payment_method` string.

Every time you add a new payment type (wallet, crypto, etc.), you must **open and modify** `PaymentProcessor`.

**Why it's bad:**
- Risk of breaking existing payment flows when adding a new one
- Class keeps growing with every new method
- Violates "closed for modification"

**Revision cue:** *"New payment method = edit the same class again"* → OCP violation.

---

## Good example — `good_example.py`

**Fix:** Define a `PaymentMethod` interface; each payment type is its own class (`UPIPayment`, `DebitCardPayment`, `CreditCardPayment`).

`PaymentProcessor` just calls `payment_method.pay(amount)` — it never needs to know which type it is.

**Why it's good:**
- New payment? Add a new class implementing `PaymentMethod`. **No change to `PaymentProcessor`.**
- Existing code stays untouched and stable
- Each payment type owns its own logic

**Revision cue:** *"Add a class, don't touch the processor"* → OCP done right.
