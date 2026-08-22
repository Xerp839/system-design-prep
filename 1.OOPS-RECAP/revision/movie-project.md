# Movie Project — Putting It Together

## What it is

A small **ticket booking system** that combines class, object, encapsulation, and abstraction ideas in one place.

File: `movie_project.py`

---

## Our example

`Movie` class manages seats and ticket booking for a film.

| Part | In our code |
|---|---|
| Attributes | `movie_name`, `total_seat`, `ticket_price`, `booked_seat` |
| Behavior | `book_ticket()`, `show_status()` |
| Hidden logic | Available seats = `total_seat - booked_seat` (caller doesn't compute this) |

---

## Which OOP concepts show up here?

| Concept | Where |
|---|---|
| **Class & Object** | `Movie` blueprint → `m1 = Movie("Odessey", 80, 800)` |
| **Encapsulation** | Seat state lives inside the object; you book via `book_ticket()`, not by editing `booked_seat` directly |
| **Abstraction** | User calls `book_ticket(4)` — doesn't need to know how availability or billing is calculated internally |

---

## Flow to remember

```
book_ticket(num)
  → check available seats
  → if enough: update booked_seat, calculate bill, confirm
  → else: reject

show_status()
  → print movie name, available seats, booked seats
```

The commented-out `show_status()` calls in the file show progressive bookings building up until the final status dump.

---

## Why this matters before SOLID

This is a **single class doing one domain job** (movie booking) — a natural stepping stone to **Single Responsibility**. If you later added payment processing, email confirmations, and database saving all inside `Movie`, you'd feel why SRP exists.

---

## Revision cue

*"One class owns the booking logic. Caller uses simple methods; internal seat math stays hidden."*
