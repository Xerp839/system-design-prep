# Single Responsibility Principle (SRP)

## What it means

**A class should have only one reason to change.**

In practice: each class does **one job**. If user data changes, only the user class changes. If database logic changes, only the repository changes — not both in the same place.

---

## Our example: User management

We model a `User` and how they get saved to a database.

---

## Bad example — `Bad Example/user.py`

**Problem:** `User` does too much.

| Responsibility | Methods |
|---|---|
| Represent user data | `get_user_info`, `is_adult` |
| Database operations | `save_to_database`, `delete_user_from_database` |

**Why it's bad:**
- Changing how we store users forces edits to the `User` class
- `User` is tied to a specific storage mechanism
- Hard to test user logic without touching database code

**Revision cue:** *"User class knows about the database"* → SRP violation.

---

## Good example — `Good Example/`

**Fix:** Split responsibilities into two classes.

| Class | Job |
|---|---|
| `User` | Holds user data + business rules (`is_adult`, `get_user_info`) |
| `UserRepository` | Handles save/delete to database |

**Why it's good:**
- `User` only changes when user-related rules change
- `UserRepository` only changes when storage logic changes
- You can swap the database layer without touching `User`

**Revision cue:** *"One class = one job. Data vs persistence are separate."*
