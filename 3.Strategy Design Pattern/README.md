# Strategy Pattern

## Interview one-liner

*"Encapsulate a family of algorithms, make them interchangeable, and let the client pick (or swap) which one runs — without changing the class that uses them."*

Same **job** (apply discount), different **ways** of doing it (Holi vs Diwali). The way is an object you plug in.

---

## Problem it solves

You have a class whose behavior varies by situation. The naive fix is:

```
if festival == "holi": ...
elif festival == "diwali": ...
```

That class then:
- grows every time a new variant appears (**OCP** broken)
- has many reasons to change (**SRP** broken)
- is hard to test one algorithm in isolation

Strategy says: **each variant is a class**. The service only knows the interface.

---

## Our example: Festival discounts

| Role | Meaning | Our code |
|---|---|---|
| **Strategy** | Contract every algorithm must follow | `DiscountStrategy.calculate_discount()` |
| **Concrete strategy** | One real algorithm | `HoliDiscount` (Diwali would be another class) |
| **Context** | Uses the algorithm, does not implement it | `DiscountService` |
| **Client** | Chooses which strategy and when to swap | `main.py` |

`DiscountService` stores the strategy privately (`__strategy`), runs it in `process()`, and can replace it with `set_strategy()`.

**Flow in `main.py`:**
1. Build Diwali strategy → inject into `DiscountService` → `process()` (Diwali logic)
2. `set_strategy(holi)` → `process()` again (Holi logic)
3. Same service object. Only the plugged-in algorithm changed.

That runtime swap is the point interviewers listen for. If you can only pick the algorithm at construction and never change it, you still have Strategy — but the stronger story is **interchangeable at runtime**.

---

## Without Strategy

All festival math lives inside `DiscountService`.

**What goes wrong in an interview story:**
- New Year sale → open `DiscountService` and add another branch (regression risk)
- Want 10% Holi on cart A and 20% Diwali on cart B at the same time → messy flags
- Unit test Diwali without dragging Holi code along → painful

**Smell:** the context class *knows how* every variant works.

---

## With Strategy

- Context: "I have a `DiscountStrategy`. I call `calculate_discount()`."
- Concrete class: owns Holi 10% (or Diwali 20%, etc.)
- New festival = **new class**, not a new `elif`

`DiscountService` is **closed** for modification, **open** for extension (new strategy classes). It **depends on the abstraction** `DiscountStrategy`, not on `HoliDiscount` (DIP). Constructor injection is the same idea as your notification-channel example.

---

## SOLID mapping (say this if they ask)

| Principle | How Strategy uses it |
|---|---|
| **SRP** | Service orchestrates; each strategy owns one discount rule |
| **OCP** | New discount = new class; don't edit `process()` |
| **LSP** | Any `DiscountStrategy` must be safely substitutable (no Holi class that throws "not implemented") |
| **DIP** | Context depends on `DiscountStrategy`, not a concrete festival class |

This is the same *shape* as Open/Closed **payment methods** — there the processor called `pay()`; here the service calls `calculate_discount()`.

---

## When to use / when not to

**Use when:**
- Several ways to do the same thing (sort, pay, discount, compress, retry)
- You need to **switch** the way at runtime (A/B test, user plan, festival calendar)
- You want to add variants without touching the caller

**Don't force it when:**
- There is only one algorithm and it will never vary — extra interface is noise
- The "strategies" aren't really the same contract (that's LSP / ISP, not Strategy)

**Cost to mention:** more classes. That's the tradeoff. Interview answer: *"We pay a few extra types to stop a god-class if/else and to swap behavior safely."*

---

## Likely interview questions

**Q: Strategy vs if/else?**  
If/else is fine for 2 stable cases. Strategy when variants grow or must be swapped/tested independently.

**Q: Strategy vs Factory?**  
- Strategy: you **already have** the context; you change **how it behaves**.  
- Factory: you **don't have** the object yet; you change **which class is created**.  
You can combine them: factory *creates* a strategy, then the context *uses* it.

**Q: Who decides the strategy?**  
Usually the client / config / feature flag — not the context. Context should stay dumb: "run whatever I was given."

**Q: Can I change strategy mid-request?**  
Yes — that's `set_strategy()`. Example: user applies a coupon after Holi default was set.

---

## Real-world mental models

- Payment: card vs UPI vs wallet (your OCP example *is* Strategy)
- Maps: driving vs walking vs transit route
- Compression: gzip vs brotli
- Games: aggressive vs defensive AI

---

## Revision cue

*"Family of algorithms → each in a class → context delegates → swap the object, not the if-else. Runtime change is the interview flex."*
