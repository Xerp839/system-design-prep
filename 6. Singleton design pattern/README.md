# Singleton Pattern

## Interview one-liner

*"Ensure a class has only one instance, and provide a global way to get that instance."*

Same object every time you "construct" it. Shared state (here: one logger, one `log_count`) lives in that single instance.

---

## Problem it solves

Some things should exist **once** in the process:
- a logger writing to one file
- a config loaded from disk
- a DB connection pool / cache

Without Singleton, `Logger("app.log")` twice = two objects, two counters, maybe two file handles. Bugs that look like "why is my log count reset?"

---

## Our example: Logger — `good_ex.py`

| Piece | Role |
|---|---|
| `Logger.__instance` | Class-level slot that holds the one object |
| `__new__` | Intercepts construction; returns the existing instance if it exists |
| `__initialized` | So `__init__` does **not** re-run and wipe `file_name` / `log_count` |
| `log()` / `get_log_count()` | Shared behavior on that one object |

**Flow to remember:**
1. `log1 = Logger("app.log")` → first time → `__new__` creates the object, `__init__` sets file + count = 0
2. `log1.log("Hey")` → count = 1
3. `log2 = Logger("app.log")` → `__new__` returns **the same** object as `log1`
4. `log2.log("Bye")` → count = 2 (not a fresh 1)
5. `log3` same story → count = 3
6. `log1/log2/log3.get_log_count()` all print **3** — proof they are one instance

If those three prints differ, it is not a Singleton.

---

## How the Python trick works (say this)

In Python, `Logger(...)` does:
1. `__new__` — allocate (or reuse) the instance
2. `__init__` — initialize it

`__new__` alone is not enough: Python still calls `__init__` on every `Logger(...)`. Without the `__initialized` guard, a second `Logger("other.log")` would reset `file_name` and `log_count` on the **same** object. Interviewers love this follow-up.

**Naive vs ours:**
- Naive: only `__new__` → one object, but init runs again → state clobbered
- Ours: `__new__` + init-once flag → one object **and** stable state

---

## SOLID — be honest

Singleton is useful and also **easy to overuse**. Interviewers respect that.

| Principle | Reality |
|---|---|
| **SRP** | Logger may also become a hidden global — "everyone talks to Logger" |
| **DIP** | Callers often `Logger()` instead of receiving a logger — hard to swap a fake in tests |
| **OCP** | The *instance* is closed; that's the point. The *class* can still grow too many jobs |

Better production shape: Singleton (or a module) **behind an interface**, injected like your DIP notification channel. The pattern is about **cardinality** (one instance), not a license for god objects.

---

## When to use / when not to

**Use when:**
- Exactly one instance is a **domain rule** (one process-wide logger, one app config)
- Creating more would be wrong (double-open the same resource)

**Don't use when:**
- You just want "easy global access" — that's a hidden dependency
- Tests need a fresh instance per test (Singleton fights you)
- You might later need **one per tenant / per request** — then it's a factory + scoped lifetime, not Singleton

**Tradeoffs to say out loud:**
- Global mutable state → order-dependent bugs
- Hard to test (can't easily replace)
- Hidden coupling: a method that never takes a logger still writes logs
- In **multi-threaded** code, `__new__` check-then-create is a race unless you lock (ours does not — mention it)

Python-specific: a **module** with `logger = Logger(...)` is already a Singleton-like. Many teams prefer that over a clever `__new__`. Still know the class form for LLD rounds.

---

## Likely interview questions

**Q: `__new__` vs `__init__`?**  
`__new__` creates/returns the instance. `__init__` initializes it. Singleton must control both or init will re-run.

**Q: Is `log1 is log2` True?**  
Yes — identity, not just equal counts. That's the check.

**Q: Thread safety?**  
Classic check-then-act race. Fix: lock around create, or `threading` / metaclass patterns. Ours is single-thread teaching code.

**Q: Eager vs lazy?**  
Ours is **lazy**: instance created on first `Logger()`. Eager: create at import time. Lazy saves work if never used; eager is simpler and avoids races at first call.

**Q: Singleton vs static class / globals?**  
Static methods have no instance state unless you fake it. Singleton is a real object (can implement an interface, be passed around). Prefer passing it (DIP) even if only one exists.

**Q: Destruction / reset?**  
Process lifetime. Tests sometimes add a `_reset()` — that's a smell that Singleton is fighting the test.

**Q: How does this differ from Factory?**  
Factory: *which* class to create (many instances OK). Singleton: *how many* of this class (at most one).

---

## Real-world mental models

- `logging.getLogger()` conceptually (one named logger)
- App `Config` loaded once
- Thread pool / connection pool (often one per process)
- Hardware: one printer spooler (GoF example)

---

## Revision cue

*"One instance via `__new__`; guard `__init__` so state isn't wiped. Shared `log_count` proves it. Say: global state, testing pain, not thread-safe unless locked. Prefer inject-the-one-instance over `Logger()` everywhere."*
