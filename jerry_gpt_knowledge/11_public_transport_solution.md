# Streamax Public Transport Solution

Distilled from the *Streamax Public Transport Solution* deck (57 slides) + speaker
script. Audience: bus & transit operators / authorities. Stock code 002970.
Credibility anchors (external-safe): **#1 in video telematics by installed base,
six years running** (Berg Insight); **5M+ vehicles in 100+ countries**; **50,000+
units in transit specifically.** Proven on fleets from Singapore to Macau to
Europe and the Americas. Company line: *"technology that builds a better
transportation future."*

**The one-line frame:** *one integrated platform, four jobs — safer driving,
smarter operations, better passenger experience, all on a single onboard system.*

A bus runs **four jobs at once**, and the pitch is that all four run on one
integrated platform (the IBCU) instead of four separate vendors / wiring / headaches:
1. **Driving Safety** — ADAS, DMS, BSD, AVM, CMCS
2. **Public Safety** — surveillance, ANPR, one-click alarm
3. **Operation Management** — driver attendance, passenger counting, scheduling
4. **Passenger Service** — ETA, route-info display, station announcements, advertising

**The all-in-one IBCU (Intelligent Bus Central Unit)** = the brain of the bus.
Instead of a DMS box + ADAS box + passenger-counter + media player + recorder all
fighting for space/power, the IBCU runs all four domains in one unit. Benefit:
lower install cost, **one cellular connection instead of four**, one system to
maintain, one source of truth. This all-in-one argument is the core differentiator —
every time a passenger screen, counter, or safety camera comes up, note it runs on
the *same* onboard device.

---

## Pillar 1 — Driving Safety

**Why:** Zero accidents is the universal goal (NYC Vision Zero, 2014). Per **NHTSA,
94% of accidents are driver error, 41% of those due to driver inattention.** Bus
driving manufactures distraction (long shifts, repetitive routes, fatigue). So the
biggest lever is watching the driver and intervening the moment attention slips.

### DMS (Driver Monitoring System) — watch the driver
Two cameras, both with **face-tracing infrared** (works in daylight, dark tunnel,
glaring backlight; adapts to glasses/masks/beards/posture). DMS warnings *prevent
risk before it escalates* — catch the lapse while it's still a lapse.

| Camera | Description | Mounting | ADAS extension |
|---|---|---|---|
| **C29N** | Pillar/dashboard DMS, cutting-edge face-tracing IR | Dashboard **or** A-pillar | No |
| **ADKIT3.0** | Dashboard DMS, expandable | Dashboard only | **Yes** (add CA20S via ADAS-extension) |

Both detect the same 6 behaviors **24/7**: **Fatigue, Distraction, Phone Call,
Smoking, Seatbelt, No-Driver.** Rule of thumb: A-pillar mounting fits your cabs →
**C29N**; want one camera that grows into ADAS → **ADKIT3.0**.

### ADAS (collision avoidance) — watch the road ahead
ADAS warnings = emergency-avoidance alerts when a collision is developing. Three
cameras, scaling in lens count:

| Camera | Lenses | Warnings | Notes |
|---|---|---|---|
| **CA20S** | Single (8mm, 42° FOV) | PCW, LDW, HMW, FCW | The workhorse foundation across a large fleet |
| **C20D** | Dual (8mm middle-focus + 2.7mm wide) | + **Near PCW** + close-range road surveillance | Wide lens covers the danger zone right in front of the bumper |
| **CA20D** | Triple (8mm + 2.7mm wide + 16mm telephoto) | + **ANPR** (plate recognition) | Flagship: full-scene awareness — collision + pedestrian + plate capture |

Warning glossary: **PCW** = Pedestrian Collision Warning, **LDW** = Lane Departure
Warning, **HMW** = Headway Monitoring (following too close), **FCW** = Forward
Collision Warning, **Near PCW** = near-field pedestrian collision warning.
Environment choice: highway/intercity → CA20S is plenty; dense urban with
pedestrians + tight stops → step up to C20D or CA20D.

**AD Safety Solution Package (3 tiers):** Basic = ADKIT3.0 + CA20S + MDVR
(immediate risk avoidance + recording); Advanced = C29N + C20D + **PT Cloud**
(now coaching drivers, building safer skills over time); Flagship = C29N + CA20D
on the **IBCU**. Three layers always: **warn, record, improve.**

### BSD (Blind Spot Detection) — the problem driver attention can't solve
A bus's own size creates blind spots no alert driver can overcome. The system
doesn't just *detect* a pedestrian — it **predicts their trajectory** ("is this
person about to step into my path?") so the alert is early, calm, and actionable.
Works in real city scenarios: crowded bus stop, busy intersection, around
fences/street furniture, low light.

| Camera | Side detection range | Road-edge | Ped. prediction | Intelligent black light | Role |
|---|---|---|---|---|---|
| **CA24S** | 15m | ✓ | ✓ | ✗ | Rear-to-front, core accident zones |
| **C46** | 16m (both sides) | ✓ | ✓ | ✓ | Top-down view, forward blind spots, start-up scenario |
| **C53** | **50m lateral** (41m forward) | ✓ | ✓ | ✓ | Flagship dual-lens, ultra-long range, black-light night |
| **AVM** | 15m (360°) | ✓ | ✗ (coverage focus) | ✗ | Around-view, narrow urban roads, 360° pedestrian warning |

- **C46** — top-down, 16m both sides, multiple VRU ID, movement prediction, road-edge recognition, tuned for the dangerous **start-up** moment (bus pulling from a stop).
- **C53** — flagship; 50m lateral matters because it lets the system track a pedestrian *early and stably* before they enter the danger zone (calm/predictive vs sudden/panic). "Black light" = works in near-darkness.
- **CMS20** — camera-monitor system (digital rear-view mirror) powered by **Blacklight 1.8T**, paired with C53 + DP12S. Four things glass mirrors can't do: (1) wider coverage incl. the new V-type mirror blind area; (2) black-light full-color night vision down to **0.5 lux**; (3) weather resistance (downward-facing lens, leeward design for rain/fog); (4) strong-light suppression via AI-ISP against glare/headlights. Plus road-edge recognition, pedestrian-intention prediction, multi-level alarms.
- **AI-AVM** — stitches multiple cameras into a seamless 360° bird's-eye view; multiple VRU ID + road-edge recognition all around; **transparent vehicle-body effect** (see "through" the bus to the wheels) + **simple calibration** (an AVM that takes half a day per bus doesn't scale).

VRU = Vulnerable Road User (pedestrians, cyclists). BSD selection: max range → C53;
full 360° for tight streets → AVM; cost-effective core → CA24S or C46.

**BSD Solution Package** runs on one of three brains by budget: **AIBOX5.0**
(lowest cost), **A8PRO V2.0** (cost-effective, full bus business), or an MDVR.
Outcomes: real-time alerts + recording + remote maintenance/evidence. The **R151**
is the ultra-long-distance solution using dual C53s. **Vision Enhancement Package**:
a C53 each side + CMS digital-mirror displays with alertors in-cab + B2 cameras +
optional MDVR → the bus effectively has no blind spots left.

**Case study — Singapore — Zero Accidents:** DMS rolled across 100% of fleet →
**zero accidents over 50,000+ km.** In one month after install, logged 4h20m of
drowsy driving across all drivers (each a near-miss caught + corrected). End-user
quote: "clear year-by-year decrease in safety incidents, drivers have better
habits, passenger satisfaction increased." (Use as the safety-pillar closer.)

---

## Pillar 2 — Operation Management (APC + OD)

**The problem:** agencies plan routes via expensive manual surveys (clipboards) or
e-payment data (only captures who tapped). Result: crowded buses at peak,
deadheading (near-empty) off-peak. The fix is real-time, accurate, automatic
passenger data.

**APC (Automatic Passenger Counting) — P3 & P3D:**
- **P3** — counts boarding/alighting at **99% accuracy.**
- **P3D** — that PLUS **OD (origin-destination) at 85% accuracy** — understands the journey (where each passenger got on AND off), not just headcount.
- Both **IP67**-rated, full certs (E-Mark, CE, FCC, REACH, RoHS) — lives above a slamming door in all weather.
- Trained on **1,400,000+ images** across every door type (inner/side/outer/folding), stair config (single/double-decker), and messy scenarios (raincoats, backpacks, luggage, bikes, wheelchairs, strollers, rain, night, crowds, queuing, doors closing mid-boarding).
- **One-click calibration:** AI auto-identifies door status → **1-second** setup. Critical for fitting a whole fleet (no per-door technician config).
- Fits mini / medium / large / double-decker / articulated buses + light rail; supports vehicles with 3+ doors.

**The attention-mechanism algorithm** (why accuracy holds in the real world): learns
to focus on features that distinguish passengers and ignore noise. Uniform scenes
(e.g., students in similar uniforms) → still tells them apart. Difficult scenes
(hat on boarding / off alighting, jacket added/removed mid-ride) → reweights toward
**stable cues** (clothing style/color) and away from changeable ones (head size,
hairstyle) → same passenger recognized boarding→alighting (this is what enables the
85% OD accuracy).

**OD data → refined operations:** analyze the network by **station** (busy vs dead
stops), **time period** (demand peaks/collapses), and **capacity** (seats run vs
people who rode), plus **Major OD** analysis (dominant trips). The passenger-flow-
vs-capacity chart (today vs same day last week) surfaces the two money anomalies:
e.g., 07:00 capacity far exceeds flow (too many empty buses, burning fuel/hours);
21:00 flow exceeds capacity (overcrowding). Both are schedule problems you can now
see and fix. The network dashboard puts the whole network on a live map with
flow analytics layered on top.

**Deployment:** Passenger Flow = **P3 + MDVR + PT Cloud** (route-station + time-period
analysis). Passenger Flow + OD = **P3D + MDVR + PT Cloud** (adds OD). MDVR options:
A16MAX / X3NPro-PT / A8Pro2.0. Easy upgrade path — start with flow, add OD without
re-architecting.

**Case study — Macau Public Transport:** solution on 70% of vehicles since 2022.
**Passengers up 36.19%** vs 2022 while the **fleet grew only 5.4%** — not more
buses, *better-used* buses (capacity matched to demand). Plus **$2.4M annual
maintenance cost savings.** (This is the operations/ROI money slide.)

---

## Pillar 3 — Passenger Service (PIS)

About the rider — the person at the stop wondering when the bus comes, and onboard
trying to find their stop. **PIS (Passenger Information System)** answers: line info
+ route ahead, transfer info, arrival & next-stop, scrolling display for live
updates, multimedia area (and advertising revenue). **Honest roadmap note: transfer
functions launch Q1 2026** — be straight about it, don't imply it ships today.

**Displays:**
- **L16MAX-286** — 28.6", ultra-wide 1920×560, 500 cd/m² (readable in direct sun), embedded or pole-mounted. For max visibility + long info strip.
- **L16MAX-215** — 21.5", full HD 1920×1080, 250 cd/m², pole-mounted. The versatile standard screen.

**PIS Box (IMS 100)** — industrial-grade onboard media player, the brain of the PIS.
Compact, drives **up to 4 screens with dual content**, OTA + USB media updates,
auto volume/brightness, compatible with MDVRs + third-party systems, managed from
one app. **Solution layers:** Screen → Player (PIS Box) → Data Source (A8Pro2.0 /
X3NPro / A16MAX) — note the data source is the *same* device family running safety
+ operations (all-in-one advantage again). At the top end, scales to **up to 7
screens** (surveillance, stop info, next-stop, line/station, promotional) — each
also an advertising surface, so this pillar can generate revenue, not just cost.

---

## Pillar 4 — Integrated MDVR + PT Cloud platform

Everything records to + connects through the MDVR (mobile recorder at the heart of
the bus). A recorder for every vehicle class, **5–24 HD channels**, large-capacity
local storage:

| MDVR | Tier | Vehicle class | Notable specs |
|---|---|---|---|
| **M1N2.0** | Basic | Mini & midi bus | 1080P, build-in storage |
| **X3NPro / X5NPro** | Advanced | Standard bus | 1080P, build-in |
| **A8Pro2.0** | High-end | Coach, double-decker | 1080P, 16 ch, AI capability expansion |
| **A16Max (IBCU)** | Flagship | Articulated, trolley bus | 24 HD ch, **6 TOPS** onboard AI computing, four-domain integration, Linux + Android multi-OS |

**Bus Operation Solution Portfolio (by capability):** **XPAD** (lightweight Android
operation screen, no heavy recording) → **X3NPro** (entry, 8 HD ch) → **A8Pro** (16
ch + AI expansion) → **A16Max** (flagship IBCU). No dead ends as needs grow.

**Exclusive operation-MDVR functions** (what makes them *operation* MDVRs, not just
recorders): (1) **Route information** — import announcement files, announce stops via
speaker as the bus passes, switch routes on-screen; (2) **Two-way PT Cloud
interaction** — send/receive messages, request operational adjustments, push
scheduling plans; (3) **Driver attendance** — clock in by card swipe or ID.

**PT Cloud modules:** every MDVR gives **Management & Maintenance** + **Safety &
Monitoring**. MDVRs *with* operation functions also unlock **Operation Business** +
full **Passenger Flow Analysis.** One platform, one login, the whole fleet — start
with safety + device health on any recorder, grow into operations + ridership
analytics with operation-capable hardware.

---

## Numbers to have cold

- #1 video telematics by installed base, 6 yrs running (Berg Insight); 5M+ vehicles, 100+ countries; 50,000+ transit units.
- 94% of accidents = driver error / 41% inattention (NHTSA).
- APC: 99% counting accuracy, 85% OD; trained on 1.4M+ images; IP67; 1-second calibration.
- BSD: C53 **50m** lateral detection; black-light full-color vision at **0.5 lux**.
- Flagship MDVR (A16Max IBCU): up to **24 HD channels**, **6 TOPS** compute, **7 screens**.
- Singapore: 100% fleet DMS → zero accidents over 50,000+ km. Macau: 70% fleet since 2022 → passengers +36.19% on a fleet that grew 5.4%, $2.4M/yr maintenance savings.

## Products in this solution (for image lookup)
IBCU (A16Max), C29N, ADKIT3.0, CA20S, C20D, CA20D, CA24S, C46, C53, CMS20, AI-AVM,
P3, P3D, L16MAX-286, L16MAX-215, PIS Box (IMS 100), M1N2.0, X3NPro, X5NPro, A8Pro2.0, XPAD.
