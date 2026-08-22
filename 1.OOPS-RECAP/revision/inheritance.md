# Inheritance (+ Polymorphism)

## What it means

**Inheritance** — a child class reuses and extends a parent class's attributes and methods.

**Polymorphism** — same method name, different behavior depending on the actual object type (method overriding).

---

## Our example — `inheritance.py`

`Dog` extends `Animal` — gets `name`, `age`, `eat()`, `sleep()` for free, then adds its own stuff.

| Part | In our code |
|---|---|
| Parent | `Animal` — name, age, eat(), sleep() |
| Child | `Dog(Animal)` — adds `breed`, `bark()` |
| Reuse parent | `super().__init__(name, age)` in Dog's constructor |
| Override | `Dog.sleep()` replaces `Animal.sleep()` — prints different message |

---

## How it works (brief)

1. `Dog` inherits everything from `Animal`
2. `super().__init__(...)` calls the parent's constructor first
3. `Dog` adds new attribute (`breed`) and method (`bark()`)
4. `dog.sleep()` calls **Dog's version**, not Animal's → **polymorphism**

```
dog.sleep()  →  "Sleeping like a dawg"   (not "I am sleeping")
```

---

## Inheritance vs Composition (keep in mind)

Inheritance = **"is-a"** → Dog *is an* Animal

Use it when the relationship is genuine. Don't inherit just to reuse code — that's a common mistake (leads to LSP violations later in SOLID).

---

## Revision cue

*"Child gets parent's stuff via `super()`. Override = same method name, different behavior = polymorphism."*
