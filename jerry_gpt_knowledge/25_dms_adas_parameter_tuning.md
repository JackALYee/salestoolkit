# DMS & ADAS Parameter Tuning — the complete settings manual

Source: *DMS and ADAS Parameter Setting User Manual*, Streamax, 12 Sep 2025.
This is the authoritative reference for **what every alarm parameter does, what
each sensitivity level actually means in seconds or metres, which setting to
recommend per haul type, and why a given false alarm is happening.**

**The premise, in the manual's own words:** AI vision has boundary scenarios —
*if the human eye cannot see the seatbelt, the AI cannot detect it either.* But
**most false positives and missed detections come from improper parameter
settings, not from the algorithm.** That is the single most useful thing to
know when a customer complains about alarm quality: tune before you escalate.

---

## 1. The four parameters on every alarm screen

**Lvl 1 Speed Range** — the speed band in which a Level 1 alarm can fire. Level 1
gives **voice + beep on the R-Watch**.

**Lvl 2 Speed Range** — starts at the top of the Level 1 band. Level 2 gives
**beep only, on the device side**.

> ⚠️ **If actual driving speed falls outside both configured bands, the DMS
> generates no alerts at all.** This is the first thing to check when a customer
> says "it isn't alarming."

**Sensitivity** — the strictness of detection, measured in **seconds** (how long
the state must persist before the alarm fires). See §2.

**Effective Time** — customisable up to **600 s**. A repeat of the *same* alarm
type inside this window is merged into the same event for platform upload,
cutting redundant records and evidence uploads **while still giving the driver
the R-Watch reminder in the cab**. That distinction matters: the driver is still
warned, the platform is not spammed.

**Do not refresh the alarm timer** — a checkbox that changes the window's shape:

| Setting | Behaviour |
|---|---|
| **Not enabled** (refresh) | Each new same-type alarm inside the window **resets the timer**, counting again from the end of the new trigger — the window trails each trigger |
| **Enabled** (do not refresh) | The window is **fixed** from the first trigger and is not extended by later triggers of the same type |

## 2. Table 1.1 — sensitivity in seconds, every DMS alarm

The alarm fires once the detected state persists this long.

| Alarm | High | Medium | Low | User-defined |
|---|---|---|---|---|
| **Fatigue** | *(see §3 — different logic entirely)* | | | |
| Distraction (L+R) | 4 | 10 | 14 | 1–60 |
| Distraction (U+D) | 2 | 3 | 4 | 1–60 |
| Yawn | 1 | 2 | 3 | 1–60 |
| Handheld device | 4 | 6 | 12 | 1–60 |
| Seatbelt | 10 | 20 | 30 | 1–60 |
| No driver | 5 | 15 | 20 | 1–60 |
| Camera cover | 5 | 15 | 20 | 1–60 |
| Smoking | 2 | 3 | 5 | 1–60 |
| No mask | 3 | 10 | 20 | 1–60 |
| Eat | 4 | 6 | 8 | — |
| Drink | 1 | 2 | 3 | — |
| Infrared block | 2 | 5 | 10 | 1–60 |

**Higher sensitivity = a shorter time = fires sooner.** Note Eat and Drink have
no user-defined range.

## 3. Fatigue — the one alarm that does not work on a timer

Fatigue uses a different algorithm depending on camera type, and **IPC and AHD
are not the same product experience.** This is a real differentiator worth
explaining to a technical buyer.

**The IPC algorithm** (C29N, AD Kit 3.0) is deep-learning based, trained on
**over 1,000,000 annotated real-world video clips**. It does **not** rely on
rules like eye-closure duration or blink frequency alone; it learns from
multidimensional cues — **gaze stagnation, eye closure, blinking,
micro-expressions and head orientation**. Inference takes **3–4 ms on the
camera's NPU**. It fires on the deep-learning probability *combined with*
cumulative eye closure. Closures count only if they last **>200 ms**.

### Table 3.1 — IPC camera fatigue logic (fires if EITHER condition is met)

| Sensitivity | Condition 1 | Condition 2 |
|---|---|---|
| **High** | probability > **0.9** AND cumulative closures (>200ms) in a **3s** window > **500 ms** | cumulative closures in a **10s** window > **2 s** |
| **Medium** | probability > **0.95** AND cumulative closures in 3s > **800 ms** | cumulative closures in 10s > **3 s** |
| **Low** | probability > **0.95** AND cumulative closures in 3s > **1000 ms** | cumulative closures in 10s > **4 s** |
| **Custom** | probability > a chosen value (**range 75%–95%**) AND cumulative closures > **800 ms (fixed)** | cumulative closures (> X×100ms) in 10s > N seconds |

### Table 3.2 — AHD camera fatigue logic (e.g. CA29M)

Rule-based, no probability term — **continuous** closure or cumulative closure.

| Sensitivity | Condition 1 | Condition 2 |
|---|---|---|
| **High** | continuous eye closure for **2 s** | cumulative closures (>200ms) in 10s > **2 s** |
| **Medium** | continuous eye closure for **3 s** | cumulative closures in 10s > **3 s** |
| **Low** | continuous eye closure for **4 s** | cumulative closures in 10s > **4 s** |
| **Custom** | continuous closure for N seconds | cumulative (> X×100ms) in 10s > N seconds |

### Table 3.3 — what each level costs you

| Sensitivity | False negative | False positive | Timeliness | User experience |
|---|---|---|---|---|
| High | Very low | **High** | Excellent | Moderate |
| Medium | Low | Moderate | Good | Good |
| Low | **High** | Low | Moderate | Excellent |

### Fatigue sensitivity by scenario

| Scenario | Recommended |
|---|---|
| Night long-haul | **High or Medium** |
| Urban congestion | **Low or Medium** |
| Highway | **High or Medium** |
| Short delivery | **Low or Medium** |
| Hazmat transport | **High or Custom** |
| Novice driver | **High or Medium** |

## 4. Distraction

**The trigger logic:** an alarm fires the instant **any sliding sensitivity-time
window contains over 80% accumulated time with the driver's eyes off the forward
roadway.** Streamax states this logic is aligned to **Euro NCAP and leading
Tier-1 practice** — a credible answer when a European customer asks whose
standard you follow.

**Distraction level by head deflection angle:**

| Level | Angle |
|---|---|
| Light | ~24° |
| Medium | 28° |
| High | > 32° |

**Judgment modes:** `L+R`, `Up+Down`, or `L+R+Up+Down`.

**Lane Departure Suppression** — when enabled, suppresses distraction alerts
during *intentional* lane changes (turning left or right), preventing
unnecessary warnings. **The option is only shown when left/right distraction is
being evaluated.** This is very likely what internal Chinese material calls
**非直道抑制** ("non-straight-road suppression"); treat that mapping as probable
but unconfirmed, and note the related but distinct turn-signal suppression in
LDW (§5.1) and "discard speed limit when turning" (§5.5).

### Distraction sensitivity by scenario

| Scenario | Recommended | Note |
|---|---|---|
| Night long-haul | High or Medium | High may interfere with necessary mirror checks |
| Urban congestion | **Medium or Low** | High gives many false alarms — urban driving demands frequent observation |
| Highway | **Medium** | High may false-alarm during navigation checks |
| Short-haul delivery | Medium or Low | High interferes with frequent turns |
| Hazmat | **High** | Low is explicitly *not recommended* |
| Novice driver | High or Medium | |

## 5. The other DMS alarms — logic and boundary cases

**Yawn** — fires when mouth-opening amplitude persists for the sensitivity time.
**Boundary case: a hand covering the mouth means no alarm** — the DMS cannot see
the mouth.

**Handheld device** — requires a detected face, then combined recognition of
*both* a hand and a mobile device. Both must be present.

**Smoking** — requires a detected face, then a cigarette detected in the mouth
area.

**No seatbelt** — image recognition of the driver's (and optionally co-pilot's)
body area; co-pilot detection only works if enabled. Two modes:
- **Normal mode** (default) — continuous
- **Regular inspection mode** — detected **once per inspection interval** (e.g.
  set 60 minutes → checked every 60 minutes). Use this to cut alarm volume where
  continuous seatbelt nagging is unacceptable.

⚠️ **Boundary case:** the system reports a seatbelt alert if the belt is **~80%
obstructed**. These false positives **can often be resolved by integrating with
DSC — supported on AD Plus 2.0.** That is a concrete upsell with a technical
justification.

**No driver** — fires when the DMS cannot continuously detect the driver's
*whole* face. ⚠️ **Designed for vehicles in motion, and it fires even when it can
see most of the face** — partial visibility means the driver is not fully
positioned in the cockpit, which is the safety risk being flagged. If a customer
finds this too aggressive, **set Low or lengthen it in User-defined**.

**Camera covering** — fires when the frame is mostly black or dark.
**Configured at:** `Config → Alarm → Video → Cover`, enabling it per channel —
**not** in the "AI APP", which is where people look first and fail to find it.

**Infrared block** — detects infrared-blocking glasses in the eye area. Worth
keeping High in almost every profile: if IR is blocked, **fatigue detection
itself is compromised**, so the driver should be told immediately.

**Eat & Drink** — recognises **burgers, hot dogs, sandwiches and toast**; for
drinks, **300–500 ml cylindrical bottles, rectangular boxed drinks, cans, and
straw-based cola** (McDonald's-style). Boundary cases: an occluded mouth may
cause a *false* eating detection, and **gloves may make hand features
unrecognisable**.

**No mask** — recognises a worn mask and alarms if the state persists.

## 6. ADAS

| Function | Sensitivity | Activates at |
|---|---|---|
| **Lane Departure Warning (LDW)** | Adjustable — see below | **≥ 20 km/h** |
| **Forward Collision Warning (FCW)** | **Fixed, non-adjustable** (critical safety) | **≥ 8 km/h** |
| **Headway Monitoring (HMW)** | 0.6–4.0 s adjustable | **≥ 28 km/h** |
| **Pedestrian Collision Warning (PCW)** | **Fixed, non-adjustable** (critical safety) | **≥ 8 km/h** |
| **Speed limit warning** | Configurable — see below | — |
| **Rolling stop** | — | Only below **50 mph (~80 km/h)** |

**FCW and PCW sensitivity cannot be tuned.** If a customer demands it, that is
a deliberate design decision on a critical safety feature, not a missing option.

### 6.1 LDW

Uses chromaticity differences in road-surface images to separate lane lines from
road, then watches for departure without the appropriate turn signal.

| Sensitivity | Trigger point |
|---|---|
| High | wheel **intersects** the lane line |
| Medium | wheel exceeds the line by **~0.1 m** |
| Low | wheel exceeds the line by **~0.3 m** |

**The left turn signal suppresses only left departure warnings; the right signal
only right.** Static-test error margin ~0.1 m. Installation variability
(height, vehicle width, side margins, front-end length) and self-calibration
inaccuracy both affect sensitivity.

### 6.2 FCW

Recognises vehicles and lane lines in the current lane, measures relative
distance, derives relative speed from positional change, and computes
**TTC = relative distance ÷ relative speed**. Fires when TTC drops below the
safe reaction + braking time, which **adjusts dynamically** with host speed and
the front vehicle's status.

### 6.3 HMW — and how it differs from FCW

Same vehicle-recognition logic as FCW. Fires when **headway ÷ host speed** is
below the set headway time **and** persists for a set duration (0.1–30.0 s),
**provided the host vehicle is continuously closing.** No warning if the gap is
held or growing.

| Standard level | Headway time |
|---|---|
| Low | 0.6 s |
| Medium | 1.0 s |
| High | 1.2 s |

**Re-arm logic:** after a warning, if headway sits between 0.2 s and 0.6 s, no
further alarm is issued **unless** headway first exceeds **1.0 s** (resetting the
warning) and then drops below 0.6 s again while closing. If headway falls from
0.6 s to **below 0.2 s**, a second warning fires immediately to signal imminent
danger.

**FCW vs HMW — the question customers actually ask:**

| | FCW | HMW |
|---|---|---|
| Purpose | Warns of an **imminent collision** | Warns you are **too close** |
| Measures | TTC = d(rel) ÷ v(rel) | time gap = d(rel) ÷ v(host) |
| Fires | Only when a crash is likely (usually < 2–3 s to impact, often much less) | **Much earlier**, when the gap drops below threshold |

### 6.4 PCW

Detects pedestrians **and cyclists** (bicycles and motorcycles) ahead, on TTC.
Displays a large red pedestrian icon. Cyclists have distinct lower-level alarm
logic but are **reported and displayed as pedestrians**.

Two deliberate non-alarms worth knowing so you don't call them bugs:
- A pedestrian/cyclist **in the lane but not in the driving path** (judged by
  vehicle width, lane lines and lane-change status) is not a collision risk — no
  alarm.
- **Steadily following a cyclist at constant speed** does not alarm. PCW is for
  highly dangerous scenarios only.

⚠️ **Range limit:** above 30 km/h, detection distance is constrained by lens
focal length — **AD Plus wide-angle lenses detect pedestrians/cyclists to
approximately 25 metres.** Above **60 km/h, PCW is not recommended.** Do not
sell PCW as a highway feature.

### 6.5 Speed limit warning

- **Warn Speed** — start warning *this many* km/h **before** the limit. Warning
  band: `limit − Warn Speed ≤ current speed < limit + Alarm Speed`.
- **Alarm Speed** — trigger the full alarm *this many* km/h **over** the limit.
  A complete alarm (beeping + red flashing icon) needs **both**: speed > limit +
  Alarm Speed, **and** that condition lasting longer than the Detection Effective
  Time. **If it is shorter, the system downgrades to a Warn Speed alert.**
- **Detection Effective Time** — how long the over-speed must persist. Typical
  useful setting **10–60 s** (avoids short-burst false alarms).
- **Big Icon Reminder Time** — how long the big red icon stays up. Typical **3–5 s**.
- **Duration** — how long the beep/voice lasts; **0 = single beep**. Typical **3–5 s**.
- **Discard the Speed Limit when turning** — disables over-speed alerts while
  turning, for a configurable number of seconds and orientation.

### 6.6 Rolling stop

Enabled only below **50 mph (~80 km/h)** — STOP signs are rare on highways, so
disabling it above that cuts false positives.

## 7. First-time configuration — the five steps and the four-week rollout

This is a ready-made professional-services narrative. Use it when a customer
asks "how do we actually deploy this?"

1. **Assess usage scenarios** — vehicle types, management needs, primary routes,
   driver experience levels, operating schedules.
2. **Configure speed ranges** — to the real driving environment. *Outside the
   configured bands, no alerts are generated at all.*
3. **Select base sensitivity** — **new customers should start at Medium**: basic
   safety assurance without excessive interruption.
4. **Set effective time** — **0–100 s** for long-haul/continuous monitoring;
   **300–600 s** for short-haul or intermittent work (balances safety with
   experience and **reduces data usage**).
5. **Test and adjust**, over four weeks:

| Week | Action |
|---|---|
| **1** | Run and record every alert: time, reason, and the driver's actual state |
| **2** | Lower sensitivity where false alarms are high; raise it where detection is weak |
| **3** | Fine-tune per driver and per route |
| **4** | Establish continuous optimisation — regular data review |

## 8. Recommended settings by haul type

### 8.1 Long-Haul Trucking
*Single trips over 500 km; 8+ hours, often at night; monotonous roads;
high-value goods. **Primary risk is fatigue.***

| Alert | Recommended | Reason |
|---|---|---|
| Fatigue | **High** | Extremely high fatigue risk needs early warning |
| Distraction | High or Medium | Simple highway environment still allows mirror checks and navigation |
| Yawning | High or Medium | Key supplement to fatigue detection |
| Handheld phone | **High** | Strictly prohibited |
| Seatbelt | **High** | Collision energy rises dramatically at high speed |
| No driver | High or Medium | DMS only activates with face detection |
| Camera obstruction | **High** | Ensures the monitoring system keeps running |
| Smoking | High or Medium | Adjust to the fleet's no-smoking policy |
| Infrared blocking | **High** | Fatigue-detection failure must alert immediately |
| Eat & drink | **High** | Adjustable per fleet |

### 8.2 Medium-Short Haul Freight
*100–500 km, 2–8 hours, mixed road types.*

| Alert | Recommended | Reason |
|---|---|---|
| Fatigue | **High** | Fatigue risk still relatively high |
| Distraction | **Medium** | Mixed roads need balance between observation and detection |
| Yawning | Medium | Supplements fatigue detection |
| Handheld phone | High or Medium | Strictly prohibited |
| Seatbelt | **High** | Serious attention under mixed conditions |
| No driver | Medium | |
| Camera obstruction | High or Medium | |
| Smoking | Medium | Per fleet policy |
| Infrared blocking | **High** | |
| Eat & drink | Medium | Allows moderate water intake |

### 8.3 Urban Delivery Services
*Express, food and supermarket delivery; short trips, frequent stops, complex
roads, high workload.*

| Alert | Recommended | Reason |
|---|---|---|
| Fatigue | Medium | Short trips → lower fatigue risk |
| Distraction | **Medium or Low** | Urban driving demands constant observation of pedestrians, vehicles, signals |
| Yawning | Medium | Basic fatigue monitoring |
| Handheld phone | **Medium or Low** | May need walkie-talkies or customer calls |
| Seatbelt | Medium or Low | Frequent entry/exit allows more time to belt up |
| No driver | Medium or Low | |
| Camera obstruction | Medium | |
| Smoking | Medium | |
| Infrared blocking | **High** | Eye-detection failure must alert immediately |
| Eat & drink | Medium | Allows moderate food intake |

### 8.4 Hazardous Materials Transportation
*Flammable, explosive, toxic or corrosive loads. **The strictest profile.***

| Alert | Recommended | Reason |
|---|---|---|
| Fatigue | **High** | Absolutely no fatigued driving |
| Distraction | High or Medium | Road observation while holding maximum attention |
| Yawning | **High** | Early detection of fatigue signs |
| Handheld phone | **High** | Strictly prohibited |
| Seatbelt | **High** | Basic safety guarantee |
| No driver | **High** | No leaving position while the vehicle operates |
| Camera obstruction | **High** | Monitoring must stay operational |
| Smoking | **High** | Strictly prohibited |
| Infrared blocking | **High** | |
| Eat & drink | **High** | Strictly limited; quick water intake if necessary |
| Mask | — | Set per hazardous-material type and protective requirements |

## 9. Troubleshooting — the six questions that actually come in

**"No driver" alert while the driver is seated**

| Cause | Fix |
|---|---|
| Driver leaning on the door, part of face outside the cockpit | Adjust sitting posture |
| Strong lighting prevents clear face detection | Boundary scenario |
| DMS cannot see the full face (not posture) | Reinstall the device |
| Lens obstructed | Remove the obstruction |

**"No seatbelt" alert while wearing the seatbelt**

| Cause | Fix |
|---|---|
| Steering wheel obstructing the belt | **Integrate DSC detection** |
| Clothing colour similar to the belt | **Upgrade to the latest algorithm version** |
| Arm or clothing heavily obstructing the belt | Boundary scenario |
| Strong light overexposure | Boundary scenario |
| Clearly belted but still alarming | Check the belt is worn properly and securely |

**Looking down at a phone triggers a *fatigue* alert** — when the driver glances
down, the eye imaging shows upper and lower eyelids nearly closed with eyeballs
not visible, so the algorithm reads it as eyes closed. **A known boundary
scenario; development is complete and validation is ongoing.** Say exactly that
— it is a known issue with a fix in flight, not a defect to deny.

**"Handheld device" alert with no phone in use**

| Cause | Fix |
|---|---|
| Holding an object shaped like a phone | Partly boundary; the algorithm filters some cases |
| Holding the steering wheel | **Upgrade to the latest algorithm version** |
| Rear or front passenger using a phone | Boundary scenario |

**Camera Cover not found in the AI APP** — it is not there. `Config → Alarm →
Video → Cover`, then enable per channel.

---

## How to use this in a sales conversation

- **"Your DMS false-alarms too much"** is usually a settings conversation, not a
  product conversation. The manual says so explicitly. Ask what sensitivity and
  effective time they are running before conceding anything.
- **The Medium default plus the four-week tuning cycle** is a concrete
  professional-services offer that competitors rarely articulate.
- **Custom fatigue mode (75%–95% probability)** is a genuine differentiator over
  rule-based fatigue detection — pair it with the 1,000,000-clip training set and
  the 3–4 ms NPU inference time.
- **Two upsells are documented here with technical justification:** DSC on
  AD Plus 2.0 resolves steering-wheel seatbelt false positives, and IPC cameras
  (C29N / AD Kit 3.0) give the deep-learning fatigue model that AHD cameras
  (CA29M) do not.
- **Do not oversell PCW at speed** — ~25 m detection on AD Plus wide-angle, not
  recommended above 60 km/h.
