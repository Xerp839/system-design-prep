# Classes & Objects

## What it means

- **Class** — a blueprint that defines attributes (data) and methods (behavior)
- **Object** — a real instance created from that class

Think: `Student` is the blueprint; `s1 = Student("Valeria", 32, "Female")` is the actual student.

---

## Our example — `classes_object.py`

We model a `Student` with name, age, and gender.

| Part | In our code |
|---|---|
| Class | `Student` |
| Constructor | `__init__` — runs when object is created |
| Attributes | `self.name`, `self.age`, `self.gender` |
| Methods | `display()`, `get_age()` |
| Object | `s1 = Student(...)` |

---

## How it works (brief)

1. Define the class with `__init__` to set up attributes
2. Add methods that operate on `self` (the object's data)
3. Create an object by calling the class like a function
4. Call methods on the object: `s1.get_age()`

---

## Revision cue

*"Class = template. Object = one real thing built from it. `self` = this specific instance."*
