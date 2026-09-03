# Decorator Pattern

## Interview one-liner

*"Attach extra behavior to an object by wrapping it in another object that implements the same interface — without subclassing every combination."*

Same type from the outside (`Beverage`: `get_description()`, `get_cost()`). Inside, wrappers **add** milk / whip / sugar on top of plain coffee.

---

## Problem it solves

You want optional add-ons that **stack**: milk, sugar, whip, and any mix.

Inheritance answer: `CoffeeWithMilk`, `CoffeeWithSugar`, `CoffeeWithMilkAndSugar`, `CoffeeWithMilkAndWhip`, … **class explosion**. That's the bad example.

Decorator answer: wrap at runtime.

```
Coffee
  → MilkDecorator(coffee)
    → WhipCreamDecorator(that)
```

New add-on = **one new class**, not a new subclass for every combo. That's OCP.

---

## Our example: Coffee add-ons

| Role | Meaning | Our code |
|---|---|---|
| **Component** | Common interface | `Beverage` — `get_description()`, `get_cost()` |
| **Concrete component** | The thing being wrapped | `Coffee` (₹20, "Plain coffee") |
| **Base decorator** | Holds the inner beverage, *is* a beverage | `AddOnDecorator` |
| **Concrete decorators** | Add one concern each | `MilkDecorator` (+₹20), `WhipCreamDecorator` (+₹50), `SugarDecorator` (+₹5) |

**Flow in `good_example.py`:**
1. `coffee = Coffee()` → "Plain coffee", 20
2. `coffee = MilkDecorator(coffee)` → description appends `", Milk"`, cost + 20 → 40
3. `coffee = WhipCreamDecorator(coffee)` → appends `", Whip Cream"`, cost + 50 → **90**
4. Print description: `Plain coffee, Milk, Whip Cream`

Calls **delegate inward**: whip asks milk, milk asks coffee, then each adds its own bit on the way out.

---

## Bad example — `bad_example.py`

`CoffeeWithMilk` **extends** `Coffee` and hard-codes "with Milk" + cost 30.

**What goes wrong next:**
- Sugar? New subclass
- Milk + sugar? Another subclass
- Whip + milk + sugar? More subclasses
- Changing milk price means hunting every combo class

**Smell:** inheritance used for **optional combinations** instead of **is-a** types.

**Revision cue:** *"New combo = new subclass"* → Decorator missing.

---

## With Decorator — `good_example.py`

Each decorator:
- **is a** `Beverage` (same methods → callers don't care it's wrapped)
- **has a** `Beverage` (`self._coffee`) — composition
- adds its slice of description + cost, then delegates the rest

**Why interviewers like this:**
- Combinations are **runtime**, not a class per mix
- Order can change: milk-then-whip vs whip-then-milk (description order; costs usually commute)
- Open/Closed: new `CaramelDecorator` without editing `Coffee`

**Honest caveat:** `AddOnDecorator` is typed as wrapping `"Coffee"` in `__init__`. Interview-perfect version wraps **`Beverage`**, so you can wrap a wrap. Your stacking in `main` already does that — say you'd type the field as `Beverage`.

---

## SOLID mapping

| Principle | How Decorator uses it |
|---|---|
| **SRP** | Coffee = base drink. Each decorator = one add-on |
| **OCP** | New add-on = new decorator class; don't edit `Coffee` |
| **LSP** | A decorated beverage must still be usable as `Beverage` |
| **DIP** | Decorators depend on `Beverage`, not on `MilkDecorator` |
| **ISP** | Tiny interface: description + cost — don't force unused methods |

---

## Decorator vs the patterns you already know

| Pattern | Question | Typical shape |
|---|---|---|
| **Decorator** | What **extra behavior** do I wrap around this object? | 1 object, **N wrappers**, same interface |
| **Strategy** | Which **algorithm** does the context run? | 1 context, **1** strategy at a time |
| **Observer** | Who do I **notify** on change? | 1 subject, **N** listeners, different role |
| **Factory** | Which **class** do I construct? | Creation, not wrapping |
| **Inheritance** | What **is** this? | Compile-time type, not runtime stack |

**Don't say:** Decorator "swaps algorithms." That's Strategy. Decorator **adds** (often stacks) responsibilities.

**Python `@decorator` functions:** same *idea* (wrap, same callable surface), different *mechanism*. In LLD they want the **object** decorator (this coffee example). Mention the name clash; then return to wrapping objects.

---

## When to use / when not to

**Use when:**
- Optional features that combine independently (add-ons, middlewares, streams: compress then encrypt)
- You would otherwise explode subclasses
- You want to add behavior **without** touching the original class (maybe you can't)

**Don't use when:**
- Only one extra feature, forever — a field/`if` is enough
- Wrappers don't share the interface — then it's just composition, not Decorator
- Order is a business rule with a fixed pipeline of 2 steps — a method might be clearer

**Tradeoffs:**
- Many small objects; debugging = peeling the onion
- Identity: `MilkDecorator(coffee) is coffee` is False — it's a new object that *behaves like* a beverage
- Constructor/setup can get noisy: wrap wrap wrap — a builder on top is OK in production

---

## Likely interview questions

**Q: Why not one `Coffee` with `has_milk` flags?**  
Flags grow into a blob of ifs (OCP). Independent stacking and reuse of add-on classes is the point.

**Q: Is `AddOnDecorator` needed?**  
It's a convenience base (holds the wrappee). Milk/Whip could wrap `Beverage` directly. Base decorator is optional but clean.

**Q: Decorator vs Proxy?**  
Same structure (wrapper, same interface). **Proxy** controls access (lazy load, auth, cache). **Decorator** adds responsibilities (milk, logging). Say intent, not class diagram.

**Q: Decorator vs Adapter?**  
Adapter **changes** the interface so another type can be used. Decorator **keeps** the interface and adds behavior.

**Q: Does wrap order matter?**  
For cost, usually not. For description / taxes / "first 100g free" rules, yes. State the order you wrap in `main`.

**Q: Can I decorate twice with milk?**  
Yes — two `MilkDecorator`s. Whether that's allowed is a business rule, not the pattern.

---

## Real-world mental models

- Coffee shop add-ons (GoF / Head First classic — yours)
- I/O streams: `BufferedReader(FileReader(...))`
- HTTP middleware: auth wrap logging wrap handler
- UI: scroll decorator around a window
- Your payment OCP example is Strategy if you *replace* pay method; Decorator if you *add* fees/logging around an existing pay

---

## Whiteboard sketch (30 seconds)

```
Beverage  ←  Coffee
    ↑
AddOnDecorator  (has Beverage)
    ↑
Milk / Whip / Sugar     each adds description + cost, then delegates
```

Client only calls `get_description()` / `get_cost()` on the outermost wrap.

---

## Revision cue

*"Same interface, wrap to add behavior. Milk(Whip(Coffee)) not CoffeeWithMilkAndWhip. Combo explosion = inheritance smell. Not Strategy (replace) — Decorator (stack). Wrap type should be Beverage, not only Coffee."*
