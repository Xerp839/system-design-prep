# Abstraction

## What it means

**Show only what matters; hide the messy implementation.**

Callers shouldn't need to know *how* area is calculated — they just need to know every shape *has* an area. You define a contract (interface) and each concrete class fills in the details.

In Python: use `ABC` + `@abstractmethod` to define abstract base classes.

---

## Our example — `abstraction.py`

We model shapes that all must provide `area()` and `parameter()`.

| Part | In our code |
|---|---|
| Abstract class | `Shape(ABC)` — can't instantiate directly |
| Contract | `area()` and `parameter()` must be implemented by subclasses |
| Concrete class | `Rectangle(Shape)` — fills in the actual math |

---

## How it works (brief)

1. `Shape` says: *"Every shape must have area and perimeter"*
2. `Rectangle` implements those methods with its own logic (`length × breadth`)
3. Code can treat any `Shape` the same way — call `.area()` without caring if it's a rectangle, circle, etc.

---

## Abstraction vs Encapsulation

| | Encapsulation | Abstraction |
|---|---|---|
| Focus | Hide **data** | Hide **complexity / implementation** |
| Question | "Who can touch this?" | "What do I need to know to use this?" |
| Our example | Private `__balance` | Abstract `Shape` interface |

---

## Revision cue

*"Abstract class = promise. Subclass = delivery. User sees `area()`, not the formula inside."*
