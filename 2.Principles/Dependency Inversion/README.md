# Dependency Inversion Principle (DIP)

## What it means

**Depend on abstractions, not concrete implementations.**

High-level modules (business logic) should not be tightly coupled to low-level modules (email, SMS, database). Both should depend on an **interface/abstract class** in between.

---

## Our example: Notification service

We send notifications via email or SMS.

---

## Bad example — `Bad Example/`

**Problem:** `NotificationService` directly creates and owns `EmailService` and `SMSService` inside its constructor.

```
NotificationService → EmailService (concrete)
                   → SMSService   (concrete)
```

**Why it's bad:**
- `NotificationService` is **hard-wired** to specific channels
- Want to add push notifications? Edit `NotificationService`
- Hard to test — can't easily swap in a mock sender
- High-level logic depends on low-level details

**Revision cue:** *"Service creates its own dependencies inside"* → DIP violation.

---

## Good example — `Good Example/`

**Fix:** Introduce `NotificationChannel` (abstract interface with `send()`). Email and SMS implement it. `NotificationService` receives any channel via constructor injection.

```
NotificationService → NotificationChannel (abstraction) ← EmailService
                                                      ← SMSService
```

**Why it's good:**
- `NotificationService` doesn't care *how* the message is sent — only that the channel can `send()`
- Swap email for SMS (or add Slack) by passing a different implementation — **no change to `NotificationService`**
- Easy to mock `NotificationChannel` in tests

**Revision cue:** *"Inject the abstraction, don't new-up the concrete class inside."*
