# Parking Lot — Learning Notes Index

`steps.md` is the article you copied from. It tells you **what** the design is.
These notes tell you **why** it looks like that, and **how to produce it yourself from a blank page.**

Read in this order:

| File | What it gives you |
| :--- | :--- |
| `01-code-walkthrough.md` | Layer-by-layer explanation of the code in `Parking Lot Design/`. Read this first, with the code open next to it. |
| `02-build-order.md` | The plan → write → plan → write recipe. The 7 passes you make over the problem. **This is the file that answers your actual question.** |
| `03-interview-playbook.md` | The 45-minute clock. What to say out loud at each minute. |
| `04-broken-things.md` | The bugs and design smells in the copied code. Fixing these is your first exercise. |
| `05-practice-drill.md` | How to practice so you can do it blank-page in 6 weeks. |

## The one-paragraph summary of the whole design

A parking lot has **floors**, floors have **slots**, slots have a **type** (bike/car/truck/EV).
A vehicle drives in, we find a free slot of the matching type, flip it to occupied, and hand back a **ticket**
(which remembers the slot and the entry time). Later the driver shows the ticket, we compute
`now - entry_time`, look up the **pricing rule** for that vehicle type, take a **payment** through some
gateway, print a **receipt**, free the slot, and kill the ticket. Everything else in that folder —
the controllers, services, repositories, adapters — is *plumbing* that keeps those five nouns
from turning into one 600-line `ParkingLot` class.

Hold onto that. If you can say that paragraph out loud, you already understand the design.
The rest is knowing where to put each line of code.
