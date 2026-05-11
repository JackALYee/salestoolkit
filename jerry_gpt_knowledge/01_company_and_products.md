# Streamax — Company, Products, Platform

## Company facts (use these verbatim where precision matters)

- **Streamax Technology Co., Ltd.** (锐明技术) — Shenzhen, China — listed SZ:002970
- Founded **2003**. AI development since **2015**.
- World's **#1 video telematics hardware provider** by Berg Insight — **7 consecutive editions**.
- **5,000,000+ vehicles equipped** across **100+ countries**.
- 2024 revenue: **CNY 2.78B (~US$385M)**, predominantly international.
- **700+ engineers**; full-stack: hardware, firmware, AI, applications, cloud.
- **4 manufacturing plants**: 2 in China, 2 in Vietnam (supply-chain resilience + non-China sourcing option).
- **500+ channel partners** across **7 industries**: trucking, school bus, public transit, mining, law enforcement, taxi, OEM.
- **8 subsidiaries**: US, Mexico, Brazil, UAE, Singapore, Japan, Netherlands, Vietnam. **180+ international staff**.
- Global hosting on **AWS + Oracle Cloud Infrastructure** in 7 regions: France, UK, Brazil, Mexico, Australia, Japan, Saudi Arabia. **GDPR**-compliant. **SSO** supported.

## Three product lines (only vendor with all three)

### A) Video telematics — Safety intelligence for the cab

**Dashcam lineup (the order to memorise):**

| Model | Price | CH | SafeGPT | CAN | Ship | Sell when |
|---|---|---|---|---|---|---|
| DS100 | $90–100 | 2 | No | No | Q1 2026 (shipping) | Price-sensitive markets, first-time adopters, Hikvision/Jimilab displacement |
| C6 Lite 3.0 | ~$130 | 3 | Yes | Yes | Q4 2026 | LCVs, vans, medium trucks, growth markets — **the volume product** |
| AD Plus 3.0 | ~$200 | 5 | Yes | Yes | Q3 2026 | Enterprise HGV fleets, Class 7–8 — **the enterprise sweet spot** |
| AD Max | ~$300 | 6 | Yes | Yes | Available | Maximum coverage needs (6CH). Value gap vs AD Plus is real today; more AI models in development. |

**CAN decode license:** $15–20 one-off per camera (all models except DS100). Activates OBD-II, J1939, FMS, Split Wire. **Always recommend CAN — it's the one-device differentiator.**

**Channel expansion:** AD Plus 2.0 supports 4CH native, expandable to 6CH via **Power Box Max**. AD Max is 6CH native. 7+ channels → MDVR.

**MDVR range:** 5-channel to 24-channel configurations + auxiliary cameras (side, rear, cargo, trailer, interior). Use cases: long-haul tractor (5ch), city bus (12ch), mining haul truck (8ch), cash-in-transit (24ch).

**Dedicated DMS — C29N (the kill shot vs Samsara/Motive/Lytx):**
- A-pillar mounted at eye level (vs DSC built into windshield-mount dashcam)
- 940nm IR — penetrates sunglasses
- 0 Lux capability (works in total darkness)
- No eyebrow occlusion when driver's head dips
- Rule-based + deep-learning fatigue (millions of real fatigue events trained)
- Available as add-on alongside any Streamax dashcam or MDVR

**All cameras include:** built-in eMMC storage, Bluetooth IoT, **Sentry Mode** (G-sensor cold-boot on impact for hit-and-run capture when parked).

**Embedded connectivity (Webbing):** optional embedded cellular across all models, launching **June 2026**. Camera ships ready to connect — no SIM sourcing.

**15-minute installation:** single cable into OBD-II / J1939 / FMS port. Power + vehicle data from same connection. AI auto-calibrates. 3–4 vehicles per hour per installer. 500-truck fleet fully deployed in one week.

### B) Visibility assistance — Regulatory compliance + operational safety

| Product | Architecture | Best for |
|---|---|---|
| **C53 BSIS** | Regulated active safety (dual-lens: side + rear/top-side) | UNECE R151/R159, European BSIS/MOIS, buses, regulated HGV |
| **C46 IPC** | Connected (LAN/MDVR-linked), remote config | On-road fleets, premium projects, platform-enabled |
| **C46A AHD** | Lightweight local (display-first), USB config | Construction, forklift, agriculture, retrofit — **fastest path** |
| **AI-AVM / 360** | Multi-camera surround, AI overlay | Large trucks, construction, premium packages |
| **CM31 / CMS** | Camera Monitor System (UN R46 certified mirror replacement) | OEM, premium truck safety, digital mirror discussions |
| **ADA family** | Local wide-angle rugged | Agriculture, harsh environments |
| **DVR/MDVR + FT Cloud** | Recording + platform | Fleet programs requiring auditability |

**Regulatory anchors:** London DVS/PSS, EU GSR2 (R151/R155/R158), UN R46 (CMS).
**CMS benefit:** 1–3% fuel savings from reduced drag + no mirror damage cost + better visibility in rain/dark/fog.
**Key insight — don't sell connectivity to a forklift customer.** Lead with C46A lightweight local for construction/forklift/agriculture. Lead with C46 IPC or C53 for on-road and managed programs. Upgrade happens naturally.

### C) Asset protection — Cargo, fuel, driver, vehicle security

**Z5 trailer camera** — standalone trailer-mounted device with own cellular + GPS:
- GPS trailer tracking (independent of tractor)
- Security camera activates on suspicious door opening
- Camera-based load volume estimation, floor-space, load duration
- Cargo fixture detection (unsecured items)
- Weight sensing integration (Q3 2026)
- **Limitation (disclose honestly):** does NOT support refrigerated/reefer trailers
- Proven verticals (anonymise externally): last-mile parcel (FedEx POC), trailer leasing, trailer OEMs (Krone POC), semiconductor (TSMC confirmed — unsecured wafer cart detection), high-value goods (Maotai confirmed — cargo switching prevention)

**Sentinel exterior camera** (NEW — June 2026) — standalone exterior-mounted, first-of-its-kind:
- Built-in cellular, GPS, storage — no cable to cab
- **Blacklight Ultra (0.02 LUX)** — clear colour video in near-pitch-black
- **Always-on Video (500mW)** — keeps recording after ignition off
- AI suspicious movement detection
- Door-opener: deploys on competitor cabs (Samsara/Lytx already there) — wedge product
- Multi-unit per vehicle (fuel tank + cargo door + toolbox), all merging on FT Cloud
- Why not a cheaper IP camera connected to MDVR? Installation labour (cable routing to cab) often exceeds hardware cost in US/EU/UK/ANZ; Sentinel eliminates that. And it works even when the cab tech belongs to a competitor.

**Facial recognition + vehicle immobilisation:**
- Continuous AI comparison of driver face vs. authorised profile
- Unauthorised driver → alert + relay activation → vehicle immobilised
- "From detect-and-report to detect-and-prevent." No other video telematics vendor offers this.

**Panic button:** one-press distress signal with GPS + two-way audio. Critical in LatAm (33% of cargo thefts involve armed hijacking).

**Honest disclosure (do not volunteer):** during hijacking, criminal groups use cellular jammers — panic button, real-time alerts, GPS, immobilisation are all blocked. MDVR continues recording locally so evidence is preserved.

## Sensor gateway (camera/MDVR as the hub)

Via Bluetooth / RS-232 / I/O:
- **TPMS** (tire pressure) — long-haul trucking, fleet tire programs
- **Fuel monitoring** — theft, efficiency, drain events
- **Temperature & humidity** — cold chain, pharma
- **Door sensors** — high-value cargo, delivery verification
- **Smoke detection** — hazmat, enclosed cargo
- **RFID / iButton** — driver authentication, cargo chain of custody
- **Alcohol breathalyser** — zero-tolerance fleets, mining, regulated
- **PTO** — construction, utility, waste management

## Platform tiers (Essential / Pro / Enterprise)

| Tier | $/veh/mo | What you get | Positioning |
|---|---|---|---|
| Essential | $1 | Livestream, GPS tracking, video playback | "I just need cameras on my trucks." |
| Pro | $3 | Essential + AI events, scorecards, coaching workflows | "I want a safety program." |
| Enterprise | $6 | Pro + SafeGPT behavioral AI, risk classification, behavioral tagging, coaching prioritization. **All future AI agent features included.** | "I want to predict and prevent accidents." |

**Upgrade path:** Essential → Pro → Enterprise is a software activation. No new hardware, no reinstallation, no data migration.

## Two integration paths for partners

- **API integration:** Streamax cameras feed data into partner's existing platform. For partners with mature platforms.
- **White-label platform:** Streamax provides complete platform under partner's brand. *"Every feature we build, you get automatically."* **Recommended.**

**Policy: no camera-only for new business.** Every new partner agreement must include API or white-label. Hardware-only is a strategic dead end — partner walls off data, AI stagnates, fleet loses deals, partner blames camera. Exceptions require Head of Sales approval.

## TSP margin reality (this is what closes deals)

| Product + Tier | TSP cost/mo | Fleet pays/mo | TSP margin/mo | Margin % |
|---|---|---|---|---|
| AD Plus 2.0 + Pro (current, 2 devices) | ~$22 | $30–35 | $8–13 | 27–37% |
| AD Plus 3.0 + Pro + CAN (1 device) | ~$16.56 | $25–30 | $8–13 | 33–45% |
| C6 Lite 3.0 + Pro + CAN (1 device) | ~$14.61 | $25–30 | $10–15 | **42–51%** |
| DS100 + Essential | ~$9.50 | $15–20 | $5–10 | 31–54% |

**Key talking point:** CAN camera improves TSP margins by 10–15 percentage points even when the TSP passes savings to the fleet. C6 Lite generates the best margins.

## What one Streamax camera replaces

| Capability | Traditional (multi-device) | Streamax (one camera) |
|---|---|---|
| Video AI (ADAS + DMS) | Separate dashcam | Built in |
| GPS tracking & trip recording | Separate GPS tracker | Built in |
| Vehicle data (speed, RPM, fuel, diagnostics) | Tracker via J1939/OBD-II | Built in — **native CAN reading** |
| Sensor gateway (TPMS, fuel, temp, door, RFID) | Separate sensor hub | Built in — **camera is the sensor hub** |
| Cellular connectivity | 2–3 separate data plans | One data plan |
| Installation | Multiple mounts, multiple wiring | One cable, 15 minutes |
