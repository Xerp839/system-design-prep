# Encapsulation

## What it means

**Bundle data + methods together, and hide internal details from the outside.**

Outside code shouldn't directly mess with sensitive data (like bank balance). Access goes through controlled methods instead.

In Python: prefix with `__` to make an attribute **private** (name-mangled).

---

## Our example — `encapculation.py`

We model a `Bank` account with a hidden balance.

| Part | In our code |
|---|---|
| Private data | `self.__balance` — can't access directly from outside |
| Controlled access | `get_balance()` — read balance safely |
| Controlled change | `deposit()`, `withdraw()` — modify balance with rules |

---

## How it works (brief)

- Balance is stored as `__balance`, not exposed publicly
- You **deposit** or **withdraw** through methods that enforce logic (e.g. check sufficient funds)
- External code can't do `account.__balance = 999999` easily

---

## Why it matters for system design

- Protects invariants (balance can't go negative without a check)
- Changes to internal storage don't break callers — they still use `deposit()` / `withdraw()`
- Foundation for SOLID — SRP and DIP build on clean boundaries between classes

---

## Revision cue

*"Hide the data (`__balance`), expose behavior (`deposit`, `withdraw`). Don't let outsiders touch internals directly."*
