# Known Gaps & Routing — what Jerry does NOT have, and where to send people

**Why this file exists.** A review of 610 logged conversations (May–Sep 2026)
found that ~8% of answers ended in "I don't have that." The refusals were
*correct* — Jerry does not invent data, and users have explicitly thanked him
for that. But the same gaps were hit repeatedly by different people, and each
time Jerry improvised a fresh "here's how you could find out" paragraph.

**This file makes those answers instant, consistent and short.** When a
question lands on something below: say plainly that it isn't held, give the
routing in one line, and move on to what *can* be answered. Do not spend
paragraphs apologising or re-deriving the workaround.

---

## 1. The single biggest gap: hardware spec sheets

Streamaxpedia is **a product index, not a spec database**. Measured: of 114
catalogued terms, 75% carry no spec-sheet URL and 41% have a description
shorter than 80 characters. The split is systematic:

| Well documented (answer freely) | Thin or empty (state the limit) |
|---|---|
| Core telematics, connectivity/eSIM, AI vision & safety concepts, compliance terms, data & metrics | **Physical hardware** — MDVR, dashcam, visibility, accessories, asset security, gateway |

**Consequence:** Jerry can reliably explain *what a capability is, which
architecture delivers it, and how to sell it*. He generally **cannot** give
lens focal length, FOV, resolution, lux rating, physical port counts,
dimensions, power draw, or box contents.

**Never estimate a hardware spec.** A wrong port count or FOV kills a bid.

### Models with NO entry at all — say so immediately

`C27` · `C28` · `XPAD 5.0` · `X5N Pro` · `A8Pro` / `A8Pro 2.0` · `A16Max` ·
`P3` · `P3D` · `CMS20` · `CA24S` · `C20D` · `CA20D`

For these, role/positioning may exist in the solution decks (school bus,
public transport) — that much can be given, clearly labelled as *positioning,
not specification*.

### Models present but with no usable description

`C40W` · `C53` · `C46` · `CA20S` — a document link may exist even where the
description does not. Give the link; don't narrate specs around it.

### Known thin entries
`CA51` (no A/D variant split) · `ADKIT` / `ADKIT 3.0` (no packing list or BOM) ·
`X3N Pro` / `X3N Pro-H0404` (architecture only, no spec sheet, no Chinese
manual) · `M1N` / `M1N 2.0`

> **CLOSED for the freight dashcam line (Sep-2026).** Full specifications for
> **AD Plus 2.0 V1.1 · AD Plus 2.0-S · C6 Lite 2.0 · C6 Lite 2.0-S · DC Max ·
> AD Plus 3.0 · DS100** now live in `22_dashcam_line_specs.md` — dimensions,
> channel counts, lens/FOV, storage, interfaces, AI combinations and power.
> Answer dashcam questions from that file. It is **Confidential**: use it to
> size and decide, never paste it to a customer. It also settles that
> **"AD Lite" does not exist**, and flags `AD Max` vs `DC Max` as an unresolved
> naming collision — DC Max is the name the spec sheet uses, and it **cannot be
> deployed without a GT1 Pro gateway**.

### Port counts — a specific, recurring trap
The validated-architecture table proves a combination **is officially
supported**. It does **not** state how many AHD or IPC ports a head unit has,
or how many remain free. Those are different questions. Never infer a physical
port count from an architecture row — send the user to the head unit's spec
sheet or to the **Sales Configurator** (`/configurator/`), which enforces
interface and channel rules automatically.

## 2. Model names that do not exist — correct the name, don't invent the product

| Asked | Reality |
|---|---|
| **"AD Lite"** | Not a Streamax model. The dashcam line is **C6 Lite / AD Plus 2.0 / AD Max**. Ask which they meant. |
| **"P3V"** | Not a model. Passenger counting is **P3** and **P3D**. |
| **"N9M"** | **Resolved (Sep-2026): N9M is the proprietary in-vehicle transmission protocol**, not a hardware model — named three times in the GDPR whitepaper (encryption in transit, IPC→MDVR, MDVR→cloud). That is why it was never in the product database. See `23_gdpr_and_data_compliance.md`. |
| **"N9M2.0"** | Still **unconfirmed as a device**. Nothing by that name exists in the product DB, solution decks, roadmap or MDVR line. **Do not guess a relationship to A8Pro 2.0 or anything else** — most likely the protocol name misread as a model. |
| **"Starry PaaS"** | Outside the Streamax portfolio. |
| **"CMCS"** | Understood as the electronic-mirror/camera-monitor capability, which lands on **CMS20** as the product. The exact expansion is **unconfirmed** — flag it rather than asserting it. |

## 3. Terminology awaiting confirmation

- **非直道抑制 (non-straight-road suppression)** — asked once, unanswered.
  Industry-general meaning: suppressing ADAS warnings such as LDW/FCW while
  the vehicle is cornering or off a straight path, to cut false alarms.
  **The Streamax-specific implementation and thresholds are not documented
  here** — confirm with the product line before quoting it to a customer.

## 4. Internal systems Jerry has no documentation for

| Asked about | Status | Route to |
|---|---|---|
| **FT OpenAPI / FT Cloud API** — endpoint list, `devsn` → `devid`, alarm-video download status enums (`NOTCONFIGURED`, `WAITING`, `DOWNLOADING`, `COMPLETED`, `FAILURE`, `DELETE`, `NOTEXIST`) | Not held. **Do not infer enum meanings from "typical" video-download lifecycles** — that was done once and was a guess. | Internal file system → FT Cloud API docs; or the platform/ops owner |
| **PT Cloud** back-office page structure | Not held. FT Cloud screenshots are **not** interchangeable with PT Cloud. | Public-transport product line |
| **R-Watch** UI, alarm icons | Not held, and Jerry cannot display images of them | Regional technical support |

## 5. Correctly out of scope — keep refusing these

These are **not** gaps to fill. The refusals are policy and must stand:

- **Internal pricing, MOQ, cost structure, quotations** → regional sales or
  partner manager. Jerry may still coach *how to handle the price question in
  the room* — that has been consistently useful and should continue.
- **CRM data, customer lists, pipelines, SMB prospect lists** → the account
  owner / regional BD. Jerry has channel-level structure, never account-level.
- **A TSP's own downstream fleet customers** (e.g. MiTac, Zonar, ORBCOMM) →
  that is the partner's private data. Structure yes, named lists no.
- **Forward sales targets** (2027 and beyond) → finance and management.

## 6. Capability limits — not knowledge gaps

- **Jerry cannot open uploaded files or attachments.** PPT/PDF/XLSX binaries
  are unreadable. Ask for pasted text. Say this immediately rather than
  attempting to work from a filename.
- **Jerry cannot display screenshots or UI images.** Naming an exact model
  *does* auto-display its product photo — use that instead of describing
  appearance, and never invent physical appearance details.
- **No live web access at answer time, no CRM, no ERP.** Knowledge is a
  snapshot; competitor financials and regulations move. State the as-of date
  on anything time-sensitive.

## 7. Answer honestly, but efficiently

The behaviour to keep: **never fabricate a number, and admit a flaw when a
user catches one.** A user challenged an unsupported competitor comparison and
Jerry conceded it immediately — that is exactly right, and it is why people
trust the tool.

The behaviour to improve: when the answer is "not held", **compress it**.
One sentence naming the gap, one line of routing, then pivot to the part that
*can* be answered well. Do not write three paragraphs of workaround.

⚠️ **Never compare Streamax against a competitor using internal release-note
deltas.** Version-log claims like "greatly improved accuracy" or "better
glasses adaptation" are measured *against our own previous build*. They are
not competitive benchmarks and must never be presented as "better than
Samsara/Motive/Lytx". No third-party DMS benchmark data is held.
