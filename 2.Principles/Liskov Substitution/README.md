# Liskov Substitution Principle (LSP)

## What it means

**Subtypes must be substitutable for their base type without breaking the program.**

If code expects a `BankAccount`, any subclass (`SavingsAccount`, `FixedDepositAccount`) should work the same way — no surprises, no crashes, no "this doesn't apply to me" exceptions.

---

## Our example: Bank accounts

Both savings and fixed deposit accounts share some behavior (deposit), but FD cannot be withdrawn from.

---

## Bad example — `Bad Example/bank.py`

**Problem:** Both `SavingsAccount` and `FixedDepositAccount` extend `BankAccount`, which declares `withdraw()` as abstract — meaning **every** account must support withdrawal.

`FixedDepositAccount.withdraw()` raises an exception: *"Cannot withdraw from FD"*.

**Why it's bad:**
- Code that accepts `BankAccount` assumes `withdraw()` always works
- Passing an FD account breaks that assumption → runtime crash
- The subclass **changes the contract** of the parent

**Revision cue:** *"Subclass throws exception for a method the parent promises"* → LSP violation.

---

## Good example — `Good Example/`

**Fix:** Split the hierarchy so subclasses only promise what they can actually do.

| Class | Can do |
|---|---|
| `Account` (base) | `deposit()` only |
| `WithdrawableAccount` extends `Account` | adds `withdraw()` |
| `SavingsAccount` extends `WithdrawableAccount` | deposit + withdraw |
| `FixedDepositAccount` extends `Account` | deposit only — never forced to implement withdraw |

**Why it's good:**
- Any `WithdrawableAccount` can safely replace another — withdraw always works
- `FixedDepositAccount` is an `Account` but not a `WithdrawableAccount` — honest type hierarchy
- No fake methods that throw exceptions

**Revision cue:** *"Don't inherit methods you can't honor. Split the interface instead."*
