# Streamax Inherent CAN Capability (Partner Enablement)

Distilled from the *Streamax Inherent CAN — Partner Enablement* deck (2026).
Headline: **vehicle CAN data, built into the dashcam you already sell.** One
device, **one $20 license**, activated remotely in FT Cloud — no separate GPS
tracker, no external CAN box, no truck-roll. A downloadable copy of this deck
is offered automatically in Jerry GPT on any CAN-bus query (name "CAN" in the
answer and a download button appears).

## The opportunity
Every fleet wants CAN data — fuel, engine health, driver behaviour, fault
codes are now expected from the box they already own. The blocker was always
**hardware**: the old way needed a **separate GPS tracker just to read CAN at
~$60/vehicle** — extra hardware to buy/ship/install, its own SIM + airtime +
power wiring, another box to fault-find, and a second data silo separate from
video.

## The shift
The **CAN decoding library is embedded directly in the AD Plus 2.0 firmware.**
The dashcam reads the raw vehicle bus and outputs clean, named parameters
on-device — no translator box between vehicle and device.
- **No separate tracker** — CAN rides on the AI dashcam already in the cab.
- **No external CAN box** — the library replaces the old power-box hardware.
- **Just a software license** — inherent capability, switched on, not bolted on.
- The extra tracker **and its SIM disappear** → one device, one SIM, one bill.

## The economics
Same data, **one third of the cost**, nothing extra to install.

| | Separate GPS tracker w/ CAN | Streamax CAN license on the dashcam |
|---|---|---|
| Cost | **$60 / vehicle** | **$20 / vehicle** |
| Hardware | dedicated tracker | none — uses the AI dashcam |
| SIM | 2nd SIM + airtime | none — shares the device link |
| Install | field install & wiring | none — activated remotely |
| Data | separate platform / silo | one platform — CAN beside video |

≈ **$40 saved per vehicle**, plus the 2nd SIM, airtime and admin go away.

## What's in it for the partner
A **high-margin software attach** across the entire installed base — a license
you switch on for dashcams already sold. Zero added BOM, zero logistics,
recognised the same way as SafeGPT and Device AI.
- **Software-margin attach** — $20 license on hardware already in the field; incremental revenue, no unit cost.
- **Sell to the installed base** — every deployed AD Plus 2.0 is a CAN upsell; no hardware re-quote.
- **Nothing new to stock** — no trackers, SIMs, or power-boxes to warehouse/ship/RMA/support.
- **Recurring & expandable** — per-device activation, unified billing, coverage grows yearly.
- Positioning line: *"You already bought the camera — turn on its CAN for $20 and skip the $60 tracker."*

## How it works
Decoded **on the device**, clean named parameters into FT Cloud:
Vehicle CAN bus (raw OEM-encoded signals) → **AD Plus 2.0** (embedded CAN
library decodes on-device) → **FT Cloud** (named parameters over the existing
link, stored vs. vehicle & driver) → **Dashboard / API** (customer sees CAN
beside video or pulls it via API). Because decoding happens in the camera,
FT Cloud gets clean labelled values — no per-vehicle backend mapping, no
external translator, and new vehicle coverage arrives as a **firmware update**.

## What you can sell — 24+ standardised parameters across 5 domains
- **Vehicle identity:** VIN, make/model/year, odometer, ignition status.
- **Powertrain & fuel:** fuel level, fuel consumption, RPM, engine temp, pedal positions.
- **Environment & state:** doors, lamps, GPS lat/long/time.
- **Safety systems:** seatbelt, DTC detection, speed, park brake.
- **Driver behaviour:** steering wheel angle, harsh accel/brake, over-rev/idling.

Exact availability varies by make/model/year — confirmed by a **per-vehicle
support lookup before you quote.**

## Use cases that close (all from one license)
1. **Fuel tank monitoring & theft** — continuous fuel-level tracking flags abnormal drops; chargeback evidence for siphoning (fuel level · ignition · GPS · timestamp).
2. **Fuel-efficient driving** — RPM + throttle + load + speed to score/coach on idling and over-revving.
3. **Driver behaviour & risk** — steering, pedal inputs, seatbelt build a risk profile complementing ADAS events.
4. **Predictive maintenance** — DTC codes + engine/battery telemetry surface issues before failure; service by condition (DTC · MIL · engine temp · battery).

## Vehicle coverage
- **3,000+ vehicle models validated & tested**; 300–500 new models added per year; 85+ countries with live deployments; 25+ years of CAN database heritage.
- Before quoting, the per-vehicle support lookup confirms where to tap the CAN bus, which parameters are available for the precise MMY, and validation status/caveats.
- **Vehicle not listed?** Two paths — wait for the batched annual coverage release, or commission an on-demand adaptation.

## Activation in FT Cloud (self-serve, no site visit)
1. **Self-serve activation** — one device from Vehicle Details, or batch from the Vehicle List.
2. **Task queued** — issued to the device; track in FT Manager → Can Activate Task.
3. **Data flows** — decoded CAN parameters appear across FT Cloud once active.
4. **Unified billing** — activated devices roll up in Report Center → Feature Activation Details.

Rollout: first on **AD Plus 2.0** (software upgrade + per-vehicle support check), more models to follow. **Requires FT Cloud V3.18.2 or later.** Workflow screens: single (Vehicle Details → CAN Status), batch (Vehicle List → More → Batch activation of CAN), progress (FT Manager → Can Activate Task), billing (Report Center → Feature Activation Details).

## Where customers see it
CAN lands next to the video: live OBD panel (Live View → Vehicle Monitoring),
full parameter view (OBD Information modal), ADAS+OBD (Alarm Detail links video
evidence to CAN context), trip playback (fuel & mileage chart with OBD timeline).

## The 30-second partner pitch
*"Your AD Plus 2.0 dashcam already reads the vehicle bus — there's no separate
tracker and no CAN box to fit. Turn on the CAN license for $20 instead of a $60
device, activate it remotely from FT Cloud, and you get fuel, engine,
driver-behaviour and fault-code data across 3,000+ vehicles — right beside the
video."* One-liner: *"Built-in CAN on the Streamax dashcam — $20 license,
activated remotely, no extra hardware."*

**Four questions partners ask:** (1) New hardware? No — AD Plus 2.0 firmware
covers it. (2) Activation? Self-serve in FT Cloud, single or batch. (3) Billing?
Per-device, same model as SafeGPT & Device AI. (4) Vehicle not listed? Annual
coverage release or on-demand adaptation.

## Downloadable asset
`Streamax Inherent CAN — Partner Enablement.pptx` — the full 15-slide partner
enablement deck. Offered as a download in Jerry GPT on any CAN-bus query.
