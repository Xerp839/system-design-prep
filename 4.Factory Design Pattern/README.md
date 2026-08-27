# Factory Pattern

## Interview one-liner

*"Centralize object creation behind a method (or class) that returns a common interface. Callers say what they need, not which concrete class to `new`."*

Factory answers: **"Who constructs this?"** — not **"How does it behave after it exists?"** (that's Strategy).

What we implemented is closest to a **Simple Factory**: one `FoodFactory.create_food(type)` with an if/elif map. Interviewers also talk about **Factory Method** (subclass decides creation) and **Abstract Factory** (families of products). If they ask which one yours is, say **simple factory**. That's honest and still valid LLD.

---

## Problem it solves

Creation logic (`if type == "pizza": return Pizza()`) is:
- duplicated if many services need a `Food`
- mixed with business logic (`prepare()`, billing, inventory) → **SRP**
- a magnet for change whenever the menu grows

Factory: **one place** knows the mapping `string → class`. Everyone else depends on `Food`.

---

## Our example: Restaurant orders

| Role | Meaning | Our code |
|---|---|---|
| **Product** | Interface of things we create | `Food` with `prepare()` |
| **Concrete products** | Actual types | `Pizza`, `Burger`, `Pasta` |
| **Factory** | Maps request → object | `FoodFactory.create_food(food_type)` |
| **Client** | Uses the product, does not construct it | `RestrauntService.create_order()` |

---

## Bad example — `bad_example.py`

`RestrauntService` does **two jobs**:
1. Decide which class to instantiate (pizza vs burger)
2. Run the order (`prepare()`)

**Interview talking points:**
- Add pasta → **modify** the restaurant service (OCP pressure on the wrong class)
- A delivery service that also needs `Food` would copy the same if/elif (DRY / consistency bugs)
- Hard to test `create_order` without constructing real `Pizza`/`Burger` (no seam to inject a fake)

**Smell:** high-level flow (`create_order`) is coupled to low-level constructors (`Pizza()`, `Burger()`). That's also a DIP miss.

---

## Good example — `good_example.py`

**Split:** factory creates, service uses.

```
RestrauntService.create_order("pizza")
        → FoodFactory.create_food("pizza")  → Pizza()
        → f.prepare()
```

Service never writes `Pizza()`. It gets a `Food` (or `None` if unknown type) and only calls `prepare()`.

**Why interviewers like this:**
- Menu change is localized to the factory (plus a new product class)
- Service can stay stable as the kitchen grows
- Return type is the abstraction — same DIP story as `NotificationChannel`

**Honest caveat (say this, it scores points):**  
the if/elif **moved**, it didn't vanish. That's OK. One factory is better than five services each with the same chain. If the map explodes, next step is a registry/dict of constructors or Factory Method — don't over-design in round 1.

---

## SOLID mapping

| Principle | How Factory uses it |
|---|---|
| **SRP** | Factory = creation; `RestrauntService` = order flow |
| **OCP** | New dish: new product class; factory is the one file you extend (simple factory still has a branch — mention it) |
| **DIP** | Service depends on `Food`, not `Pizza` |
| **LSP** | Every product must honor `prepare()` — no dummy that throws |

---

## When to use / when not to

**Use when:**
- Many places would otherwise `new` the same family of types
- The concrete class depends on a string, config, or user input
- You want to hide constructors (complex setup, caching, later swap to another implementation)

**Don't use when:**
- You create one class in one place once — `Pizza()` is clearer
- You use a factory to hide a 20-line constructor that should just be a builder / better `__init__`

**Tradeoff:** extra type (`FoodFactory`). Benefit: a single creation seam for tests and future change.

---

## Factory vs Strategy vs Observer (don't mix them in the round)

| Pattern | Question it answers |
|---|---|
| **Factory** | Which **object** do I create? |
| **Strategy** | Which **algorithm** does this object use? |
| **Observer** | Who should I **notify** when state changes? |

Combo that sounds senior: factory **creates** a `DiscountStrategy`, `DiscountService` **runs** it.

---

## Likely interview questions

**Q: Why not `if` in the service? It's the same if in the factory.**  
Because creation is now **one responsibility in one type**. Other services reuse it. Tests can mock the factory. The service reads as "get food, prepare" — domain language, not construction.

**Q: Simple Factory vs Factory Method?**  
- Simple: one class, one method, switch/map (ours).  
- Factory Method: `Creator` subclasses override `create()` — used when each product line has its own creator hierarchy.  
Don't claim Factory Method unless you have that hierarchy.

**Q: What if `create_food` returns `None`?**  
That's a design choice. Interview-safe: prefer raise / Result type over silent `None`, so the caller doesn't call `prepare()` on nothing. Your good example already checks `None` before `prepare()`.

**Q: Does Factory violate OCP because of the if?**  
Slightly, in simple factory. We **contain** the violation in one class instead of spreading it. That's a standard, acceptable answer.

---

## Real-world mental models

- `NotificationFactory` → Email vs SMS vs Push (ties to your DIP example)
- Logger factory → file vs console
- DB driver from connection string
- UI: `ButtonFactory` for iOS vs Android (Abstract Factory if you need a *family*: button + checkbox + dialog)

---

## Revision cue

*"Caller names a type; factory returns the interface. Service never `new`s Pizza. If/else lives once, in the factory — that's Simple Factory."*
