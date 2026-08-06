# Sentinel (S5) — the public microsite + the authoritative spec

**Sentinel** is the market-facing name. **S5** is the model number. They are the
same product — the docs are filed as `S5-*`, the deck as `Sentinel-*`. Use
"Sentinel" with customers, "S5" when quoting, ordering, or talking to support.

This file covers the public microsite and the official specification. The
selling *strategy* for Sentinel — why it is the wedge product, the door-opener
argument against Samsara/Lytx cabs, the market-by-market theft picture — lives
in `05_visibility_and_security.md`, and the portfolio entry in
`01_company_and_products.md`. Don't restate those here; cross-reference them.

---

## The microsite — https://streamax-sentinel.com

A public, customer-facing single-page site owned by Streamax. **Nothing on it is
confidential and no login is required**, so it is safe to send to a prospect,
paste into an email, or drop in a chat.

**Send the link when:**
- A prospect wants something to circulate internally after a call — it is far
  better than a PDF attachment and always current.
- They ask "show me what it actually sees at night" — the site has an
  interactive 0.02-lux comparison (smartphone vs standard night cam vs Sentinel)
  that lands harder than any spec line.
- They want to understand the AI — there is a live 3D posture-detection demo
  where you can walk a figure past the truck vs send it to the fuel tank.
- A partner or reseller asks for collateral: the Docs section has the deck and
  all three manuals, downloadable without a gate.
- You need the field results in the customer's own hands (see below).

**Don't** send it instead of a conversation. It is a fuel/cargo-theft story for
parked trucks — if the customer's pain is driver behaviour or compliance, the
microsite is off-message and will re-anchor them on the wrong problem.

### What you can download from it

| Document | Link | Size |
|---|---|---|
| Product Presentation (deck) | `https://streamax-sentinel.com/Docs/Sentinel-Product-Presentation.pptx` | 3.8 MB |
| Product Specification | `https://streamax-sentinel.com/Docs/S5-Product-Specification.docx` | 0.4 MB |
| User Manual | `https://streamax-sentinel.com/Docs/S5-User-Manual.docx` | 3.8 MB |
| Installation Guide | `https://streamax-sentinel.com/Docs/S5-Installation-Guide.docx` | 1.5 MB |

### The site's own positioning

> "Sentinel is the industry's first **Always-on Video** camera — purpose-built to
> guard parked trucks. The forensic clarity of a camera at the power budget of a
> sensor. Engine off, still watching, for up to 90 days."

The framing is a 2×2 of forensic clarity × power efficiency: video-based
products give clarity without endurance, sensor-based products give endurance
without evidence, and the top-right corner was empty until Sentinel. That is a
good whiteboard structure — it makes the category, not just the product.

Six features as the site names them: **Always-on Video**, **Intent-Aware AI**,
**Black Light Ultra**, **All-in-One Design**, **IoT Synergies**, **Minutes to
Install**.

On the AI, the site's language is worth borrowing verbatim:

> "Motion alone is noise — animals, headlights, rain, a passer-by. Sentinel reads
> body posture and behaviour, so it can tell someone walking past your truck from
> someone working at your fuel tank." … "Every alert arrives with the footage.
> Not a notification to go investigate — the evidence itself."

---

## ⚠️ Where the microsite and the spec sheet disagree

**Three headline numbers on the public site do not match the official S5
specification.** Quote the spec sheet in anything technical, contractual, or
written into an RFP response. If a customer quotes the website back at you,
do not argue on the call — say you will confirm against the specification.

| Claim | Microsite says | S5 Product Specification says |
|---|---|---|
| AOV standby power | "~400 mW" | **"In AOV mode: about 500MW"** |
| Low-light performance | "Full color at **0.02 lux**" | **"Minimum Illuminance — Color: 0.05 Lux/F1.2"** |
| Installation | "tool-free… **any driver** can deploy or reposition it" | **"requires installation by professionals"**, and the AI needs a strict calibration procedure |

**Power is a real conflict.** 500 mW is also the figure already carried in
`00_jerry_persona.md` and `01_company_and_products.md`, so the microsite's
~400 mW is the outlier. Quote 500 mW. It is also the conservative number, which
is the right way to be wrong when a customer is sizing battery drain.

**Lux may not be a conflict — but confirm before you assert either way.** The
0.05 Lux/F1.2 line sits under *"Parameters of road facing lens"*, i.e. the bare
sensor's minimum illuminance, while 0.02 lux is quoted for **Black Light Ultra**,
which is the AI-ISP processing layer on top (the spec lists "AI-ISP, Support
black light" separately under Backlight Compensation). Sensor floor vs
processed-output figure is a normal and legitimate distinction. Treat 0.02 lux
as the Black Light Ultra claim and 0.05 Lux as the raw lens parameter, and if a
technical buyer presses on which applies to their scene, get Product Marketing
to confirm rather than improvising.

Flag both to Product Marketing rather than quietly picking numbers — a public
site and a public spec sheet should not need this footnote to reconcile.

---

## Authoritative specification (from S5-Product-Specification.docx, © 2025)

**Imaging** — single built-in ultra-wide lens, 1/2.8" 2 MP CMOS, 1920×1080 @
30 fps, focal length 1.9 mm, **HFOV 175° / VFOV 92°**, shutter 1/30–1/100000 s,
minimum illuminance colour 0.05 Lux/F1.2, digital WDR, AI-ISP with black light
support, S/N ≥42 dB, H.264/H.265 (default H.265), VBR/CBR (default VBR).

**Note the sensor is 2 MP.** "Forensic clarity" on the microsite is about colour
at night, not resolution — don't let a customer infer 4K. Against a 4K-camera
objection the honest answer is that colour and usable detail in near-darkness
beats more pixels of black, and the 175° lens covers the whole flank.

**Storage** — 1 × Micro SD, up to 1 TB. Video supports **AES256 encryption**.

**Connectivity** — 4G **Cat1** (plug-in Nano SIM; reserved eSIM position and
pre-burn-in eSIM supported, but **plug-in SIM and eSIM cannot be used at the
same time**), Wi-Fi **2.4 GHz only** (802.11 a/b/g/n), GNSS: GPS L1, Galileo
E1B/C1, GLONASS L1OF, SBAS (WAAS/EGNOS/MSAS/GAGAN). Inertial navigation module
built in.

> **Deployment gotcha — an industrial SIM (MP2) is mandatory.** The spec states
> plainly that a standard SIM (MP1) is prohibited and Streamax is *not
> responsible for issues caused by using one*. Raise this in any deal where the
> customer supplies their own SIMs; it is a common and expensive field failure.
> See `14_esim_solutions.md` if eSIM is on the table.

**I/O** — 1 × RS232, 1 × IO input, 1 × IO output, 1 × USB Type-C. This is what
the microsite means by "IoT Synergies": fuel, tyre-pressure, temperature and
door sensors feed in and every alert carries video.

**Sensing** — 6-axis gravity sensor: harsh acceleration, harsh deceleration,
harsh cornering, collision detection.

**Power** — 12 V and 24 V self-adaptive. AOV mode ≈ **500 mW**; typical ≈ 3.2 W
(SD + SIM dialling); full load ≈ 5 W (streaming preview over 4G + Wi-Fi).
Optional built-in battery rides through a power cut for **5 minutes only** —
it is a graceful-shutdown buffer, not a power source. **The "up to 90 days"
standby runs off the truck battery**, so the real qualifying question is the
state and capacity of that battery, and whether the fleet is comfortable with a
~500 mW parasitic draw.

**Environment** — IP69K. Operating −40 °C to +70 °C without battery, −30 °C to
+60 °C with the battery fitted (**the battery option narrows the temperature
range** — matters for Middle East and Nordic deals). Storage −40 °C to +85 °C.
Humidity 15–95 % non-condensing. In direct sun the surface can exceed 60 °C.

**Physical** — 121.2 × 106.6 × 92.9 mm, 290 g net (640 g packed).

**Platform** — embedded Linux. UI languages: English (default), Chinese,
Spanish (LatAm), Portuguese (LatAm), French, Russian, Japanese.

**AI features as the spec lists them** — human posture detection for theft
identification, suspicious person detection, suspicious target detection,
vehicle contact inspection, vehicle collision detection.

---

## Installation reality — three mounts, and calibration is not optional

The Installation Guide documents **three** methods, not one:

1. **Screw-fixed** — secure the base, clip the device on, fasten with screws.
2. **Magnetic** — attach the magnetic bracket to the device's rigid base, then
   to a ferromagnetic surface. This is the "tool-free" path the microsite
   advertises, and it needs the magnetic bracket accessory.
3. **RAM mount** — secure to pre-drilled mounting points.

Two things the microsite's "minutes to install" glosses over, and you should
not:

- The specification says the product **requires installation by professionals**,
  citing risk of electric shock, vehicle wiring damage, degraded AI performance
  and device detachment.
- **Sentry camera calibration must be performed strictly to procedure** — point
  marking and calibration on the vehicle body area first, then the rest. The
  guide is explicit that skipping it stops the system getting accurate image
  information and reduces detection accuracy.

So: fast compared with routing cable to the cab (which remains the real
argument, per `05_visibility_and_security.md`), but not a driver-slaps-it-on
product if you want the AI to work. Set that expectation before the pilot, or
the customer will blame the AI for a calibration failure.

---

## Field proof — already public, so quotable by name

Both cases are published on the microsite by Streamax, so unlike the anonymise-
externally rule for POC accounts in `01_company_and_products.md`, **these two
can be named**. They are the strongest fuel-theft proof points available.

- **Ampenet · Tanzania** — an employee siphoning fuel, caught in the **first
  month** on the vehicle. The customer went from **2 test units to 17**, and now
  markets Sentinel into their own market. Use this for the land-and-expand
  story, and for the reseller conversation.
- **Texas · Kenya** — on one truck, monthly fuel losses fell from **$206 to $5**.
  **Two-month payback at a $400 unit price.**

The site frames these as "already running on customer fleets across Africa and
the Middle East… timestamped, GPS-tagged, and handed to the customer as
evidence."

> **On the $400.** It is a public, case-specific reference price for that
> deployment — not a price list and not a global number. Quote it as "in that
> deployment the unit price was $400 and payback was two months", never as
> "Sentinel costs $400". Real pricing follows the usual channel and clearance
> rules; internal pricing discussion stays leadership-only.

The Kenya case is the cleanest ROI arithmetic in the portfolio: a single truck,
a two-month payback, a number the customer can check against their own fuel
spend. When a prospect asks for business case rather than product, lead here and
let them substitute their own litres.
