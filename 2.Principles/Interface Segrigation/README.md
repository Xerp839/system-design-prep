# Interface Segregation Principle (ISP)

## What it means

**Don't force a class to implement methods it doesn't need.**

Split large, fat interfaces into smaller, focused ones. A class should only depend on the methods it actually uses — not a bloated contract with irrelevant methods.

---

## Our example: Workers vs Robots

Both can work, but only human employees eat. Robots don't.

---

## Bad example — `bad_ex.py`

**Problem:** One fat `Employee` interface with both `eat()` and `work()`.

- `Worker` implements both — fine
- `Robot` must implement `eat()` too, but raises an exception: *"Robot can't eat"*

**Why it's bad:**
- `Robot` is forced to implement something meaningless
- Callers might call `eat()` on any `Employee` and crash on a robot
- Same smell as LSP — broken contract, but the root cause here is an **over-sized interface**

**Revision cue:** *"Robot forced to implement eat()"* → ISP violation.

---

## Good example — `good_ex.py`

**Fix:** Split into two small interfaces.

| Interface | Method |
|---|---|
| `Workable` | `work()` |
| `Eatable` | `eat()` |

- `Robot` implements only `Workable`
- `Employee` implements both `Workable` and `Eatable`

**Why it's good:**
- Each class only commits to what it can do
- No dummy or exception-throwing methods
- Callers that need eating behavior use `Eatable`; callers that need work use `Workable`

**Revision cue:** *"Small interfaces. Class picks only what it needs."*
