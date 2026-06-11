# Streamax School Bus Solution (2026)

Distilled from the *2026 Streamax School Bus Solution* deck (33 slides) + speaker
script. Audience: school districts, operators, transport authorities. The
emotional through-line is **"Known, protected, never left behind"** — and the
brand promise is *"we protect the smile of 2 billion children."* Streamax serves
**500,000+ school buses** worldwide and is global #1 in video telematics by
installed base.

The solution has **three safety pillars** plus a platform layer:
1. **Attendance** — palm-vein recognition: knowing exactly which child boarded.
2. **Stop-arm violation capture** — protecting kids from traffic while boarding.
3. **Child check** — guaranteeing no child is ever left behind on the bus.

Frame each pillar as a standalone ~10-minute conversation; lead with whichever
matches the buyer's mandate.

---

## Operation overview — four stages of a bus run

| Stage | Capabilities |
|---|---|
| **Attendance** | Palm-vein student attendance, attendance snapshot, student info pushed to platform + parents |
| **Driving** | Arrival notification, stop-arm violation detection, route-info display, AI active safety |
| **Arrival** | Child-check system, off-board student list |
| **Management** | Live video, live GPS tracking, live AI alarm, route management, alarm/violation evidence management |

Five core capabilities: full-HD surveillance, child check, arrival notification, driver active safety, route management.

---

## Pillar 1 — Attendance via Palm Vein Recognition

**The problem with RFID cards** (the legacy approach): kids forget them (→ manual
checks), lose them (→ replacement fee + tracking gap), cards can be **copied**
(security liability with children), and high management cost (purchase, register,
distribute, replace across thousands of students). Mature and accepted, but
fragile and expensive.

**Palm vein** = the child's own hand. The reader identifies the unique vein
pattern beneath the skin using **850nm near-infrared light**. Why it fits buses + kids:
- **Ultra-fast matching** — line keeps moving at a busy stop.
- **Unique & stable pattern** — doesn't change as the child grows (unlike face/fingerprint surface); no two alike.
- **Anti-spoofing by nature** — only recognizes a real, living palm (reads blood vessels). Can't be photographed or copied onto a card.
- **Non-contact** — more hygienic, no shared surface.
- **360° omnidirectional** — swipe in any direction, instant read (matters with kids, not trained adults).
- **Forget-proof, lose-proof, copy-proof.**

**Proven, bank-grade technology** — palm vein is already used in **electronic
payments** (pay with your palm) and **access control** (secure gates/doors). If
it's reliable enough to move money and guard restricted entrances, it's reliable
enough to confirm a child is on the bus.

**What parents get (Dynamic Perception of the Student Trip):** the moment a child
swipes to board, the system captures a snapshot and pushes a notification to the
parent's phone — child is on the bus, here's the picture, time and stop. Same on
alighting. The bus tracks live counts (e.g., "West stop: onboard 10 / offboard 9").
No more anxious parents calling the school.

**Architecture (how it works):**
- **Registration (one-time):** student identities imported into **SBS Cloud** → pushed down to the device on the bus.
- **Recognition (everyday):** child swipes reader → reader checks onboard records → DVR confirms match → result goes to cloud + parents.
- Device **stores up to 6,000 students locally** → instant recognition, works even with poor connectivity. The cloud is the system of record; the bus doesn't need a live connection to know who boarded.

---

## Pillar 2 — Stop-Arm Violation Capture

**The scale of the problem:** NASDPTS one-day count — 98,065 school bus drivers
across 35 states observed 66,322 motorists illegally passing a stopped bus *in a
single day*. Extrapolated over a 180-day school year = an estimated **45.2 million
illegal passing violations per year** nationwide (US). This is one of the most
dangerous moments in a child's day — exactly when kids are crossing to board/alight.

**The solution** captures the violation automatically with **court-grade
evidence**: records the vehicle, reads the plate, logs time + location, packages
an evidence file in the platform. Example penalty: **$300 fine, −6 license points**.
The goal isn't the ticket — it's deterrence so the next driver thinks twice.

**Capture hardware (three specialized devices):**
- **C28** — AI Detection Camera: sees the violation, triggers capture.
- **C27** — License Plate Camera: tuned to read plates cleanly even at speed (makes evidence enforceable).
- **B2** — Audio-Visual Alarm: alerts in the moment.

**Scaled by road width:**
- Capture kit = C28 + 2–4× C27 (plate cameras) + 2× B2 → feeds an MDVR.
- **2–4 lane road → X3N** MDVR.
- **5–8 lane road → X5N Pro** MDVR (more plate cameras to cover every lane).
- Evidence flows to **SBS Cloud**, OR via **open API** directly into a third-party
  police/municipal audit platform. The API matters — Streamax slots into the
  authority's existing enforcement system.

**Case study — Abu Dhabi:** capture since 2020, now **10,000+ buses**. Before: couldn't
identify violators, couldn't penalize, stop rule had no teeth. After: complete
evidence to traffic police → real penalties → deterrent. **2–3 tickets/bus/month.**
Business model: operator purchases + installs devices, police review evidence +
issue fines, operator collects a **service fee** on captured violations → safety
system with a revenue stream attached.

**Case study — United States:** capture since 2020, now **40,000+ buses**. Same
before/after. **~8 tickets/bus/month** (reflects the 45M/year problem). Business
model: **share-of-fines** — revenue shared back funds equipping more buses → more
captures → more children protected. A virtuous cycle: safety that funds its own
expansion.

---

## Pillar 3 — Child Check (no child left behind)

**The tragedy:** a child left in an enclosed bus for just **30 minutes at 38°C**
can suffer severe heat stroke, suffocation, death. Last-10-years deaths of students
left behind on school buses: **USA 221, Japan 12, UAE 45.** Every one was preventable.

**How it happens (two failure points):**
- **Before locking:** driver leaves without a proper inspection.
- **After locking:** a sleeping child (often small, slumped below the seat line) isn't seen, left inside for hours.

**The three-layer solution (deploy one, two, or all three — layers save lives):**

**Solution 1 — Driver inspection button (behavioral layer).** Before locking, the
driver must walk to the **back of the bus and press a check button** — and on the
way passes every seat. *That walk is the inspection.* Press = clean check logged.
Skip it and try to lock = alarm triggers + uploads to platform. Behavioral design:
the safe action is the only action that doesn't set off an alarm. Builds inspection
into muscle memory. The three principles: **Remind** inspection, **Report** to
platform if not checked, **Force** a double-check.

**Solution 2 — AI camera (vision layer): C34 / CA34.** Solves the hardest case — a
child who isn't moving at all. **92% accuracy.** Detects: head slumped below seat
back, child lying across the aisle, only part of a body visible, child wearing a
hat that hides their face, etc. Looks for a *person*, not motion → finds the
sleeping child a glance would miss. **Fully automatic:** driver leaves → AI
auto-enables → scans the locked empty bus → if it finds someone, raises AI alarm
→ office notified → driver called back to re-check.

**Solution 3 — High-precision motion sensor (redundancy layer): DP7S.** **99.9%
accuracy**, low-power (watches for hours after shutdown without draining battery),
long-duration aisle monitoring. High sensitivity to movement *inside* the cabin,
high anti-interference from *outside* (a person walking past in the lot doesn't
false-trigger). After the bus is locked and engine off — the exact moment a
forgotten child becomes endangered — the sensor stays awake and catches any
movement. Deployed with an **X3N recorder, alarm horn, GPS, 4G**.

**Emergency response chain:** AI camera detects remaining student → alarm fires
locally (horn) AND remotely to ops center → operator sees live picture + map
location → calls driver back / dispatches nearest person. Minutes matter in a hot
vehicle.

**Case study — UAE:** "radar version" since 2018, **8,000+ vehicles**. Config:
driver inspection before locking + high-precision radar detection after. Result:
helped drivers build the inspection habit, and **no such accidents have occurred**
on equipped buses. Not reduced — none.

**Case study — adding AI vision:** since 2023, **300+ vehicles**, full three-layer
stack (inspection + radar + AI camera). Same outcome: **no such accidents.**

---

## Platform — All-in-One + SafeGPT

All three pillars run as one all-in-one solution alongside AI blind-spot detection,
driver-behavior monitoring, route management, student-attendance management. Tied
together by **SafeGPT**, the cloud behavioral-AI engine — what separates Streamax
from a camera vendor. SafeGPT:
- **Prioritizes critical risks** — team focuses on what matters, not alert noise.
- **Driver profiling + coaching by purpose** — targets each driver's specific weak points.
- **Real-time accident identification & response.**

A program that gets smarter over time and a workforce that genuinely improves — not
a hard drive of footage nobody watches.

---

## Four product tiers (match to regulation + budget)

| Tier | Product | What's included |
|---|---|---|
| **1 — Most cost-effective** | **M1N 2.0** | Child Check + Attendance + Surveillance + SBS Cloud. Covers the two life-safety pillars (who's aboard + nobody left behind). |
| **2 — Added capabilities** | **X3N** | Tier 1 + **AI IPC** (AI intelligent cameras) for smarter onboard detection / AI-vision child check. |
| **3 — Regional regulatory** | **X5N Pro** | Child Check + **SAV** (surround/active-safety vision) + Surveillance + AI IPC + SBS Cloud. Channel capacity for stricter mandates (e.g., wide-road stop-arm capture). |
| **4 — Every scenario (flagship)** | **IBCU** (Intelligent Bus Central Unit) | Child Check + Attendance + Surveillance + **Operation** + SAV + AI IPC + SBS Cloud. One brain running the entire bus. |

**Tier cheat-sheet:** M1N 2.0 = core/cost-effective · X3N = adds AI cameras · X5N Pro = regional regulatory compliance · IBCU = all-in-one flagship.

---

## Numbers to have cold

- 500,000+ school buses served; protect the smile of 2 billion children.
- Palm vein: stores **6,000 students** locally; 850nm near-infrared; 360° omnidirectional.
- Stop-arm: **45.2M** illegal passing violations/US school year; US **40,000+** and Abu Dhabi **10,000+** capture buses; US ~8 tickets/bus/mo, Abu Dhabi 2–3/bus/mo; example penalty $300 / −6 points.
- Child check: motion sensor (DP7S) **99.9%** / AI camera (C34) **92%** accuracy; hot-car fatal at 30 min / 38°C; 10-yr deaths USA 221, Japan 12, UAE 45; UAE 8,000+ since 2018 with **zero** such accidents.
- **Honest framing on accuracy:** the AI camera is 92% — which is exactly why it's *layered* with the driver button + the 99.9% motion sensor. Redundancy is the point; no single layer is the whole safety case.

## Products in this solution (for image lookup)
C28, C27, B2, C34/CA34, DP7S motion sensor, palm-vein reader, M1N 2.0, X3N, X5N Pro, IBCU.
