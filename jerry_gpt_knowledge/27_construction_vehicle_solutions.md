# Construction vehicle visibility solutions — current selection and engineering reference

Distilled on 23 October 2026 from the three owner-supplied originals below.
The configuration/SKU baseline is dated 22 October 2026; recorded software
evidence is dated 21 October. This is internal Streamax reference knowledge.
It supports sales selection and technical explanation, not automatic ordering,
signed QA approval, certification or a customer-ready quotation.

## Source authority and how to answer

The originals are in `Construction vehicle solutions/`:

1. **01_Construction_Solution_Configuration_and_BOM.xlsx** (S1): 11 sheets.
   `Routes` owns canonical C01–C11 definitions. `02_Master_SKUs` owns the 47
   current part numbers. `BOM Data`, `Regional SKUs`, `Cable Options`,
   `Customer Fit Guide`, `Ownership TCO` and `Pre-Send Checklist` support selection.
2. **02_Construction_Architecture_Route_Matched_Engineering_Diagrams_EN.pdf**
   (S2): 12 pages. Route-matched topology, original drawings and corrective notes.
   PDF page numbers below are physical pages, not the decorative ROUTE labels.
3. **03_Technical_Compatibility_and_Validation_Matrix.xlsx** (S3): 8 sheets.
   `01_Route_Baselines`, `02_Interface_Compatibility`, `03_Validation_Matrix`,
   `04_Software_Versions`, `06_Open_Validation`, `07_Verification_Policy` and
   `08_Canonical_ID_Audit` distinguish known configuration from missing proof.

For construction vehicle / construction machinery / jobsite blind-spot and
visibility questions (工程机械、工程车辆、工地车辆、施工车辆、挖掘机、装载机、盲区、可视化),
start with the distilled recommendation and explain why it fits. Use the user's
language. Ask only the missing facts needed to select a route: machine/model and
country, hazard zones/camera positions, 2/4/5 camera need, waterproof display,
vehicle power/IO and cable runs, recording/storage and whether cloud is required.
Do not force cloud into a local-viewing requirement or treat a regional SKU as
proof of regulatory approval.

For complicated/multi-part requests, full BOMs, cable/pinout questions,
installation, firmware compatibility or validation, give a concise answer plus
**all three original documents** for download. Explicitly name **construction
vehicle solutions** (or 工程车辆可视化方案) so the interface attaches their buttons.
On follow-up requests for the files, repeat that topic. Explain which original
to consult: S1 for selection/BOM/TCO; S2 for topology and drawings; S3 for evidence
and open actions. Cite sheet names/rows or PDF pages. The downloads are the
unchanged original XLSX/PDF files, not newly generated summaries. Identify them
as internal references; a combined customer kit still needs ERP/PDM review or
Product Manager sign-off. Never invent a download URL, exact pinout, price,
certification, detection range/accuracy or approved firmware release.

**Precedence:** for this construction solution, the current S1 master and S3
interface/baseline tables plus S2 corrective annotations supersede older generic
visibility pitches, legacy drawings and S3 `05_Source_Trace` historical excerpts.
Historical ST1/ST2 IDs are audit context, not current customer route numbers.
Historical source C07 means an aggregate M3N reference; current **C07 means M1N
two cameras**. Do not transfer old test assertions to the new route by ID alone.
S3 open-action B02 writes `C07/03/04` while its description concerns M1N 2/4/5;
use canonical **C07/C08/C09** from S1/S3 baselines and flag the action-cell
cross-reference for engineering reconciliation. Action C04's `C02 / 03B` likewise
uses a historical suffix: current connected routes are C02/C03. Do not silently
treat stale action IDs as a new hardware configuration.

## Choose the visibility approach

Source: S1 `Customer Fit Guide` rows 5–9; `Routes` rows 5–15; S2 pp. 10–11.

- **C46:** flexible mounting for localized hazard zones on construction vehicles,
  on-road vehicles or forklifts; scenario-specific on-device AI and active alerts.
  The standard detailed routes use C46 IPC, not AHD. Coverage and suitability
  depend on the actual installation and configured application.
- **C53:** focused long-side plus **front blind spot on the same side**; intended
  front mounting is essential. Do not describe it as an arbitrary mid-side mount
  or automatic all-around coverage. System/vehicle-specific approval evidence is
  required before making a BSIS regulatory claim.
- **AI-AVM / 360°:** calibrated bird's-eye surround view for the driver's checks
  before movement and during low-speed turns; especially intuitive for drivers
  familiar with car surround view. Do not assume every AVM includes AI detection.
  C46 is optional per project, not part of the four-CA51 reference by default.
- **CM31/CMS:** OEM-specific indirect-vision assistance with C53/DP12S in the
  reference concept. No blanket claim that physical mirrors may be removed.
- S1's compute ordering (C53 highest, C46 middle, AVM lower) is qualitative only;
  it is not a benchmark of TOPS, latency, safety or detection accuracy.

## Five detailed construction routes: C06–C10

Source: S1 `Routes` rows 10–14 and `BOM Data`; S2 pp. 1–9; S3 `01_Route_Baselines`.
All use standard **C46 IPC 5152178100023**, chosen display and BA5 outputs.
These are specified configurations; formal QA evidence is tracked separately.

| Route | Host / region | Cameras and topology | Kit / purchasing difference | PDF |
|---|---|---|---|---|
| C06 | M3N H0404 North America, **5120121100005** | 4 C46, **four direct native IPC paths**, no switch | HDD enclosure included, actual HDD/SSD excluded; current 20-pin harness, power and regional antennas in kit | pp. 2–3 |
| C07 | M1N 2.0, choose region/enclosure SKU | 2 C46, **two direct native IPC paths**, no external switch | BA5-I optional at two zones; no storage drive included | pp. 5–6 |
| C08 | M1N 2.0, choose region/enclosure SKU | 4 C46, **all four through one external switch** | Switch **5173002100003 ×1** plus drive cable **1261020000036 ×1**, separately ordered | pp. 7–8 |
| C09 | M1N 2.0, choose region/enclosure SKU | 5 C46, **one direct IPC + four through one switch** | Same one switch + one drive cable as C08; five cameras do NOT all pass through the switch | pp. 7, 9 |
| C10 | M3N H0204 EU/Asia, **5120182100013** | 4 C46, **four direct native IPC paths**, no switch | Includes **1 TB SSD**, enclosure, GPS/4G/Wi-Fi and current 20-pin cable; **no MicroSD card**; not standard NA kit | pp. 2–3 |

C08/C09 need **no additional separately ordered switch-power accessory**.
M1N H0402 has 4 AHD + 2 native IPC; switch expansion gives the documented 4/5
C46 IPC routes. H0404 has 4 AHD + 4 IPC; H0204 has 2 AHD + 4 IPC. The generic
M3N drawing's ADAS/DMS/expansion options do not mean those features or additional
cameras are included in C06/C10. Camera quantities are per vehicle; positions
must follow its hazard zones. The C09 drawing repeats the label C46-Right: confirm
the fifth actual zone, rather than claiming a universal duplicated right-side layout.

## Six project-reference routes: not standardized orderable construction kits

Source: S1 `Routes` rows 5–9, 15; S2 p. 11; S3 baseline and verification policy.

| ID | Reference architecture | Boundary |
|---|---|---|
| C01 | C46 AHD **5152178100020** + local display/alarm | Local jobsite blind-spot warning; no fixed MDVR kit; AHD-specific power/video/wiring |
| C02 | C46 IPC + regional MDVR + FT Cloud | Connected video/alerts/fleet management; verify region, licensing and end-to-end operation |
| C03 | C53 BSIS + CA51 + B3A + MDVR + FT Cloud | Front-mounted C53 monitors long-side/front same-side hazards; project compliance evidence |
| C04 | AI-AVM/360° + **4×CA51** + MDVR/dashcam | Calibrated bird's-eye observation; processor, interfaces and actual AI functions per project |
| C05 | CM31/CMS + C53 + DP12S | OEM-specific indirect vision; mirror-replacement approval is vehicle/region-specific |
| C11 | C46 + local display/alarm | Local pedestrian/object hazard reference; choose AHD 0020 or IPC 0023 with its own signal path |

Forklift/warehouse and agriculture references are opportunities to scope, not
extra released construction kits. Agriculture ADA/C46A records have no additional
canonical C ID. Never turn these concepts into a complete ready-to-order BOM
without project-specific design and review.

## Current components, quantities and inclusion rules

Source: S1 `02_Master_SKUs` rows 15–51 and `Cable Options`; S3
`02_Interface_Compatibility` rows 5–17; S2 pp. 10, 12.

**Cameras**
- Standard C46 IPC **5152178100023**: 6-pin RS765-6 direct connection; standard
  bracket and screws included. **The camera's RS765-6 output connector is not
  waterproof.** Official outdoor-joint protection remains an open evidence item.
- C46 IPC **5152178100017**: waterproof M12 12-pin camera interface; includes
  adapter **1261010100072** (M12-12 male → RS765-6 female + 5559-6P, 300 mm),
  rain bracket **1120041100679** and tool **1160060100013**. Adapter tails still
  require installation protection. For **C06 this is PoC fallback only when 0023
  is unavailable**, not an approved production substitution.
- C46 AHD V1.1 **5152178100020**: M12 8-pin/AHD; not interchangeable with IPC
  0017/0023 or their wiring. C46A terminology in local concepts does not change that.

**Alarms**
- **BA5-O 5164003100004 ×1 per vehicle** is standard, ordered separately;
  exterior light and 5W speaker, fixed audio, current M12-4 RS485 + DJ7061-6 IO.
  Alone it uses the standard host harness directly, with no dual-alarm adapter.
- **BA5-I 5164002100004 ×1** is strongly recommended when **more than two
  blind-spot zones** are monitored; optional otherwise. Four-direction visual
  indication plus 5W fixed audio. Do not call it mandatory on every vehicle.
- If **both BA5-I and BA5-O** are installed, separately order
  **1261050100490 ×1 per vehicle**, including on C07 if the optional BA5-I is chosen.
  It is not bundled with the alarm or host.
- Optional extensions: **1260010100265, 3 m**, waterproof M12-4, shared with
  DW7P; **1260040100475, 7 m**, confirmed compatible with current BA5 setup.
  The latter has a legacy 6-pin mini-5557 description; exact physical adapter/
  pin path is drawing-dependent, not permission to invent pin equivalence.

**Choose one display**
| Need | Model / SKU | Power and separate items |
|---|---|---|
| No waterproof requirement, Streamax logo | DP7S **5146026100001** | MDVR power; separate **1210030000163** 3 m cable |
| No waterproof requirement, no logo | DP7S **5190012100084** | MDVR or independent vehicle power; same separate **1210030000163** cable |
| Waterproof display required | DW7P **5146054100001** | MDVR or vehicle power; bracket/base lead included; optional 3 m extension **1260010100265** separate |

Do not quote both DP7S variants and DW7P together as mandatory items. Optional
DP7S sunshade: **1130040100051**. A waterproof display does not make all camera
connectors or the whole installation waterproof.

**Camera extensions: choose actual measured runs, not a universal seven metres**
| Length | Current RS765-6 extension SKU |
|---|---|
| 3 m | 1260010000351 |
| 5 m | 1260010000352 |
| 7 m | 1260010000353 |
| 11 m | 1260010000355 |
| 15 m | 1260010000357 |

The 7 m cable has the source's R118 flame-retardant marking; this is not whole-
vehicle certification. L=4M/L=7M labels in old drawings are illustrative, not
current orderable cable SKUs. **1260010100168** is an old 7 m reference, not the
current default. Current M3N 20-pin harness **1261050100539 is included in both
H0404/H0204 kits**: do not double-order. Old **1261050100409** and generic 22-pin
depictions are not that cable and do not establish an equivalent pinout.

**Commissioning and optional parts**
- Easycheck **5190001000009** is a temporary Wi-Fi maintenance dongle used with
  Veyes; **one per solution/commissioning team, not one per vehicle**. The same
  workflow applies to M1N/M3N 2/4/5-camera setups, with camera-count configuration
  changed. No additional dedicated calibration device is specified.
- C46 service configuration lead **1261010100077** is optional as needed; it is
  not the 0017 installation adapter. Optional magnetic mount **3380000100102**,
  extension bracket **3380000100124**, extra 8-output IO lead **1210010100070**.
- **3320000100504 is an M1N heated HDD enclosure**, not a camera adapter, despite
  the old installation-guide label (S3 `03_Validation_Matrix` row 81).

## Exact regional host and in-kit references

Source: S1 `Regional SKUs` rows 5–14; `02_Master_SKUs` rows 5–14, 35–43.

| Host | Region | With enclosure | Without enclosure |
|---|---|---|---|
| M1N 2.0 | North America | **5110038100014** | **5110038100037** |
| M1N 2.0 | EU/Asia | **5110038100028** | **5110038100029** |
| M1N 2.0 | Latin America | **5110038100004** | **5110038100038** |
| M3N H0404 | North America | **5120121100005** | Not specified |
| M3N H0404 | EU/Asia | **5120121100004** | Not specified |
| M3N H0404 | Latin America | **5120121100003** | Not specified |
| M3N H0204 | EU/Asia (C10) | **5120182100013**, includes 1 TB SSD | Not specified |

Select exactly one regional host; all listed M1N and H0404 kits exclude the
actual HDD/SSD. Enclosure is not a drive. H0204 is not a standard North America
substitute: prefer C06/H0404 for NA and escalate exceptions to Product Manager.
Historical Europe M1N **5110038100228** is not current **5110038100028**; do not
substitute it or infer equivalence. Do not resurrect old H0204/SKU candidates
from S3 source archives as current order lines.

S1 marks these M1N/H0404 items as included, so avoid duplicate procurement:
power+CAN1 **1261070100016**; 4G antenna **1210050100055** (two in NA, one other
regions); Wi-Fi **1210050A00015**; enclosure lock key **1170040000004**;
7.5A fuse **1060970000006** and 15A fuse **1060970000005**. GNSS differs:
M1N **3130000100065**, H0404 **1630002100012**. Verify actual chosen package;
these part-number mappings are not automatically an H0204 package inventory.

## Software and validation: what is known versus what is still open

Source: S3 `04_Software_Versions` rows 5–11, `03_Validation_Matrix`,
`06_Open_Validation`, `07_Verification_Policy`.

Recorded identifiers, **not a prescription to install or a production-release approval**:

| Component | Recorded identifier | Evidence boundary |
|---|---|---|
| M1N 2.0 | HY_M1N2.0_M0010_V3.5.10_RC26090160 | Separate M1N record; signed 2/4/5-camera combination evidence needed |
| C46 | ST_966C46_E228965_V3.5.9_R26082702 | Reported integration; exact SKU/test scope/region proof pending |
| Veyes | Veyes_1.6.3.apk | Recorded maintenance app; device/OS/test scope not documented |
| B5A / BA5 | B5-P01-STM32-MCU-T26092401.T26100939.CRC | File-list version 1.0 is not established firmware release version; confirm I/O and current 0004 coverage |
| M3N | HY_M3N_M0010_V3.5.10(1).12_D26101902_DEBUG | Reported shared H0204/H0404 software and delivery; DEBUG filename does not prove approved mass-production release |
| Display | No separate software version, per supplied confirmation | Not applicable |
| Platform | Not supplied | Service/integration scope remains a separate check |

S3 retains **108 validation checks and 16 open evidence actions**. Important
open items: external 0023 joint and 0017 adapter-tail weather protection; approved
H0204 connection/configuration and current 4/5-camera drawings; signed production
firmware and M1N/M3N/C46/current-BA5 integration; multi-alert/recording/recovery
performance; actual-vehicle power, IO, installation and acceptance; exact country/
carrier approvals; C53 BSIS applicability; CMS/OEM mirror-replacement approvals;
AVM calibration and AI scope; FT Cloud region/licensing/end-to-end tests; and
authorized regional commercial terms. A source statement that a configuration
is deliverable does not supply those missing reports. Explain the particular gap
relevant to the question rather than claiming everything is untested or approved.

The PDF contains native drawing excerpts with annotations, not a final released
20-pin pinout. For pin-level work, parking-brake/reverse IO, polarity, pulse/level,
fuses, voltage, calibration geometry or safety acceptance, provide S2 and S3 and
route the specific unresolved item to Product/FAE/QA. Do not turn legacy example
IO1/IO2 assignments or cone counts into universal installation instructions.

## Installation effort, ownership cost and release

Source: S1 `Ownership TCO` rows 2–7, 11–36; `Pre-Send Checklist` rows 5–11.

One 2026 M3N + four C46 + display + BA5-I/O project used **2 installers ×3 hours
+ 1 installer ×4 hours = 10 person-hours**. The stages took about seven effective
elapsed work hours across two calendar days. This is a single project example,
not a guaranteed installation time or a universal labour rate.

Use customer/local inputs: hardware, separately ordered accessories, regional
hourly labour rate, other installation cost, deployment/training, annual cloud,
annual maintenance, vehicle count, ownership years and a single currency.
Blank means unknown, not free; zero means a confirmed zero-cost item.

- Installation labour = person-hours × regional hourly rate.
- One-off per vehicle = hardware + external accessories + installation labour
  + other installation + deployment/training.
- Annual recurring = cloud/platform + maintenance.
- First-year TCO = one-off + annual recurring.
- Period TCO = one-off + annual recurring × years; fleet TCO = period TCO × fleet size.
- Undiscounted; taxes, financing and downtime are not automatically included.

Release sequence: select canonical route and vehicle inputs → choose actual
camera/cable/display/alarm options → reconcile quantities and included items →
**recheck the complete assembled BOM in ERP/PDM or obtain Product Manager
approval** → issue the approved customer kit/quotation. Separate QA, production
software and regional/country evidence must support any claims made. No prices,
MOQ, warranty or lead-time defaults are supplied here; retain Jerry's existing
pricing clearance and use authorized regional terms.
