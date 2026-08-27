# Observer Pattern

## Interview one-liner

*"Define a one-to-many dependency: when the subject changes state, all registered observers are notified automatically. The subject depends on an Observer interface, not on TV or mobile classes."*

Also called **publish–subscribe** at a small scale. Subject = publisher. Displays = subscribers.

---

## Problem it solves

Object A changes. Objects B, C, D must react. Naive code:

```
self.tv.show(temp)
self.mobile.show(temp)
```

Then:
- new display → edit A (**OCP**)
- A imports every UI (**DIP** inverted — high-level weather depends on low-level screens)
- can't plug a display in/out at runtime (user closes the TV app)

Observer: A holds a **list of Observer**. On change, loop and call `update()`. B and C register themselves (or a compositor does).

---

## Our example: Weather station

Temperature is the shared state. TV and mobile must show the new value.

| Role | Meaning | Our code |
|---|---|---|
| **Subject / publisher** | Owns state, owns the list, notifies | `WeatherStation` |
| **Observer interface** | What every listener must implement | `Observer.update(temp)` |
| **Concrete observers** | Each reacts its own way | `Tvdisplay`, `Mobile_display` |
| **Client / wiring** | Creates pieces and subscribes | `main.py` |

Station methods:
- `add_obeserver` / `remove_observers` — manage the list
- `update_temp` — write `__temperature`, then `notify()`
- `notify` — for each observer, `update(self.__temperature)`

**Flow in `main.py`:**
1. Create station, TV, mobile
2. Subscribe both
3. `update_temp(30)` → both print their own "temp updated to 30"

One write, many reads. That's the demo to walk through on a whiteboard.

---

## Without Observer

Station would hold `Tvdisplay` and `Mobile_display` as fields and call them by name.

**What breaks:**
- Watch / website / logger → more fields, more imports, more edits
- Testing temperature logic requires real displays
- Removing the TV still leaves dead calls unless you remember to delete them

**Smell:** subject **knows concrete subscribers**.

---

## With Observer

- Station only knows `Observer`
- TV and mobile don't know each other
- Subscribe/unsubscribe without changing `update_temp()`

Encapsulation: temperature is `__temperature`. Observers don't poke it; they receive it in `update()`. That's the same "hide data, expose behavior" idea as your bank example — applied to a **broadcast**.

---

## SOLID mapping

| Principle | How Observer uses it |
|---|---|
| **SRP** | Station: state + notify. Each display: how to show |
| **OCP** | New display = new `Observer` + `add_obeserver`. Don't edit `notify()` |
| **DIP** | Station → `Observer` abstraction, not `Tvdisplay` |
| **LSP** | Every observer's `update` must be safe to call (no "I don't support this" throw) |
| **ISP** | Interface is tiny: just `update`. Don't force displays to implement unused methods |

---

## Push vs pull (common follow-up)

| Style | What happens | Ours |
|---|---|---|
| **Push** | Subject sends the data in `update(temp)` | Yes — we pass `temp` |
| **Pull** | Subject sends `update(self)`; observers call `get_temperature()` | Not in this code |

**Say:** push is simple when the payload is small (one number). Pull is better when observers need different slices of a large state (some want temp, some want humidity) so you don't stuff 10 args into `update`.

---

## When to use / when not to

**Use when:**
- One state, many interested parties (UI widgets, logs, cache invalidation, event listeners)
- Set of listeners is **dynamic**
- You want to decouple "what happened" from "who cares"

**Don't use when:**
- Only one consumer, forever — a direct call is clearer
- You need a guaranteed order / transaction across listeners (Observer is usually fire-and-forget)
- A chain of "if this then that then that" with one path — might be Chain of Responsibility, not Observer

**Tradeoffs to mention:**
- Notification order is often undefined (we loop a list — order = registration order, but don't rely on it unless you document it)
- A slow observer blocks others if `notify` is synchronous (ours is sync `for` loop)
- Risk of **memory leaks** if you add observers and never remove (classic UI bug)
- Risk of **update storms** / cascading notifies if observer A updates the subject again

---

## Observer vs Strategy vs Factory

| | Observer | Strategy | Factory |
|---|---|---|---|
| Relationship | 1 subject → **N** observers | 1 context → **1** strategy (at a time) | Creator → **1** product |
| Typical verb | notify | delegate | create |
| Runtime change | add/remove listeners | `set_strategy` | different `food_type` string |

Don't say Observer is "for swapping algorithms" — that's Strategy.

---

## Likely interview questions

**Q: Who calls `add_observer`?**  
Usually the client (`main`) or the observer registering itself. Subject should not construct TV/mobile internally (that would recouple).

**Q: What if an observer throws?**  
In production you'd catch, log, continue — otherwise one bad display kills the rest. Our example doesn't; mention that as a gap if they probe.

**Q: Observer vs events / message queue?**  
Same idea, different scale. In-process list = Observer. Kafka/SQS = distributed pub/sub. Interview LLD: Observer is the in-memory pattern.

**Q: Can the subject be an observer too?**  
Possible but easy to get cycles. Prefer a clear one-way: weather → displays.

**Q: Difference from MVC?**  
Views are often observers of the model. You can mention it; don't overclaim.

---

## Real-world mental models

- Spreadsheet cell changes → charts refresh
- Button click → many listeners
- Stock ticker → dashboards
- `addEventListener` in the browser
- Your notification DIP example *could* grow into Observer if many channels must all fire on one event (vs Strategy/DIP where you pick **one** channel)

---

## Whiteboard sketch (30 seconds)

```
WeatherStation                 Observer (update)
  - observers[]                    ↑
  + add / remove              Tvdisplay    Mobile_display
  + update_temp() → notify() → update(t)   update(t)
```

---

## Revision cue

*"1-to-N: subject stores observers, on change loops `update()`. Subject never imports TV/mobile. Push vs pull, sync notify, remember unsubscribe."*
