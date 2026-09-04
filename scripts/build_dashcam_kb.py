"""Regenerate jerry_gpt_knowledge/22_dashcam_line_specs.md from the spec workbook.

    python3 scripts/build_dashcam_kb.py

Jerry's loader only globs `*.md`, so an .xlsx sitting in jerry_gpt_knowledge/ is
invisible to him. This turns the workbook into the markdown he actually reads.
Re-run it whenever the workbook is updated rather than hand-editing the .md,
so the specs can never drift from the source.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl is required:  pip install openpyxl")

ANALYSIS = """## How to choose, in one line each

| If the requirement is… | Propose |
|---|---|
| Cheapest compliant ADAS + driver monitoring, 2 cameras | **C6 Lite 2.0** |
| Same, but the cab camera is refused (privacy/works council) | **C6 Lite 2.0-S** — no internal lens, DMS added externally |
| The volume workhorse: ADAS + DSC built in, room for 2 more cameras | **AD Plus 2.0 V1.1** |
| Workhorse without the cabin lens | **AD Plus 2.0-S** — ADAS + external DMS |
| Highest spec available today, 1520P both lenses, black-light road view | **DC Max** — but read the GT1 Pro warning below |
| Smallest / lowest power, OBD-powered, quick install | **DS100** (~4W loaded) |
| A 2026 refresh with GNSS L1+L5 and 2×CAN | **AD Plus 3.0** — *not launched*, do not quote a date |

## Three things that will cost you a deal if missed

**1. DC Max is not a standalone device.** Its network, GPS, Wi-Fi, 3G/4G antenna
and I/O all read *"Requires cascaded GT1 Pro"*. It cannot be deployed without the
GT1 Pro gateway, and the product database records GT1 Pro as **currently
restricted to sell in the USA**. Quote DC Max as a two-box solution and confirm
the GT1 Pro is sellable in the region before proposing it anywhere.

**2. "AD Max" and "DC Max" are two entries for what looks like one product —
confirm the name before quoting.** The product database carries *both*: `AD Max`
("Flagship 6-channel AI dashcam", no gateway mentioned) and `DC Max`
("6-channel AI dashcam used with GT1 Pro. Cannot be individually deployed
without GT1 Pro"). This authoritative spec sheet only knows **DC Max**, and its
GT1 Pro dependency matches. The risk is concrete: a rep reading the `AD Max`
entry would quote a standalone flagship and omit the gateway entirely. Treat
**DC Max** as the correct name, flag `AD Max` as unverified, and have the
product line kill one of them.

**3. Side-view BSD ships without the algorithm.** On AD Plus 2.0, AD Plus 2.0-S
and DC Max the side-view BSD line reads *"BSD algorithm software currently not
supported"* — the camera mounts and records, the detection does not run. The
overhead BSD on DC Max is different: the **C46 includes a black-light BSD
algorithm**. Do not sell side-view BSD as a working detection feature today.

## What separates the -S variants

`-S` means **no internal (cabin) lens**. Consequence: no built-in DSC — the DSC
row is empty for both -S models. They are for one-channel ADAS plus an
*external* DMS camera, which is the configuration to reach for when a fleet or
works council refuses an integrated cab-facing camera but still needs driver
monitoring.

## What this file does NOT settle

- **AD Plus 3.0** is *Not launched* and its sheet still says "To be
  supplemented" for dimensions, G-sensor frequency, antennas, pulse, BSD
  cameras, R-Watch and all power figures. Its ADAS description also carries the
  note *"as stated in the initial specification"* — treat every 3.0 number as
  provisional and never put one in a quote.
- **Pricing** is not here and never will be — regional sales owns it.
- **Bill of materials / box contents** for the expansion kits, brackets and
  cabling are not in this sheet.
- The DMS lens row for **C6 Lite 2.0-S** lists CA29P and two different CA29M
  options; the recommended part is **CA29P (4mm, 50–100cm)**.
"""

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "jerry_gpt_knowledge" / "Dashcam_Series_Comparison_EN_New_Models.xlsx"
OUT = ROOT / "jerry_gpt_knowledge" / "22_dashcam_line_specs.md"
SHEET = "Dashcam Comparison (EN)"

MODEL_COL_START = 4          # column D holds the first model
NAME_ROW = 5
FIRST_SPEC_ROW = 6


def clean(v) -> str:
    if v is None:
        return ""
    return " ".join(str(v).replace("\n", " ").split()).strip()


def load():
    ws = openpyxl.load_workbook(SRC, data_only=True)[SHEET]
    models = [clean(ws.cell(NAME_ROW, c).value)
              for c in range(MODEL_COL_START, ws.max_column + 1)]
    models = [m for m in models if m]

    # Column A/B/C carry a 3-level label that only fills in when it changes.
    rows, group, sub = [], "", ""
    for r in range(FIRST_SPEC_ROW, ws.max_row + 1):
        a, b, c = (clean(ws.cell(r, i).value) for i in (1, 2, 3))
        if a:
            group, sub = a, ""
        if b:
            sub = b
        # Key on the FULL path, not the leaf. "Type" appears under both
        # "GPS Positioning" and "Storage"; keying on the leaf alone made the
        # second silently overwrite the first and printed the SD-card spec as
        # the GPS type.
        key = "|".join((group, sub, c))
        values = [clean(ws.cell(r, MODEL_COL_START + i).value)
                  for i in range(len(models))]
        if any(values):
            rows.append((key, values))
    return models, rows


def md_escape(s: str) -> str:
    return s.replace("|", "/")


def build() -> str:
    models, rows = load()
    by_key = dict(rows)
    if len(by_key) != len(rows):
        raise SystemExit("duplicate spec keys — the workbook layout changed")

    def row(key: str) -> list[str]:
        if key not in by_key:
            raise SystemExit(f"spec row not found in the workbook: {key!r}")
        return by_key[key]

    L: list[str] = []
    add = L.append

    add("# Dashcam Line — Full Specifications (freight market)")
    add("")
    add("> **HANDLING — read before using anything below.** The source workbook is")
    add("> classified **Confidential**, audience *\"Sales and Technical Personnel in the")
    add("> Sales Region\"*, and states: **\"Can this table be released directly to")
    add("> customers: No. Key information must be reduced and processed before")
    add("> release.\"**")
    add(">")
    add("> So: use these numbers to size a solution, answer an internal question, or")
    add("> decide what to propose. **Do not paste this table, or a block of these")
    add("> specs, into a customer email, quote or deck.** Give the customer the two or")
    add("> three figures their requirement actually turns on, and let the official")
    add("> datasheet be the document that reaches them.")
    add("")
    add("Source: `Dashcam_Series_Comparison_EN_New_Models.xlsx`. Regenerate with")
    add("`python3 scripts/build_dashcam_kb.py` — do not hand-edit this file.")
    add("")

    # ── the line-up ─────────────────────────────────────────────────────────
    add("## The line-up")
    add("")
    add("| Model | Positioning | Status |")
    add("|---|---|---|")
    pos, status = row("Product Positioning||"), row("Product Status|Status|")
    for i, m in enumerate(models):
        add(f"| **{m}** | {md_escape(pos[i])} | {md_escape(status[i]) or '—'} |")
    add("")
    add("**That is the whole freight dashcam line.** If a model is not on this list,")
    add("do not invent it — check the name. In particular **\"AD Lite\" is not a")
    add("Streamax product**; someone saying it means C6 Lite 2.0 or AD Plus 2.0.")
    add("")

    # ── per model ───────────────────────────────────────────────────────────
    add("## Model profiles")
    add("")
    KEY = [
        ("Applicable Scenarios||", "What it is"),
        ("Product Form|External Dimensions (mm)|", "Dimensions (mm)"),
        ("Audio/Video|Video Input|", "Video input"),
        ("Audio/Video|Maximum Video Resolution|", "Max resolution"),
        ("Audio/Video|Video Output|", "Video output"),
        ("Storage|Type|", "Storage type"),
        ("Storage|Storage Medium/Maximum Capacity|", "Storage capacity"),
        ("Communication|Network Communication|", "Network"),
        ("Communication|Communication Module|", "Regional variants"),
        ("Communication|WIFI Function/Antenna|", "Wi-Fi"),
        ("GPS Positioning|Type|", "GPS"),
        ("Interface|Serial Port|", "Serial"),
        ("Interface|I/O|", "I/O"),
        ("Interface|CAN|", "CAN"),
        ("Interface|Supported CAN Data|", "CAN protocols"),
        ("Interface|USB|", "USB"),
        ("Interface|External Screen|", "External screen"),
        ("Interface|UPS Power Box|", "UPS / expansion box"),
        ("AI|ADAS|Configuration", "ADAS"),
        ("AI|ADAS|Lens Specification", "ADAS lens"),
        ("AI|ADAS|Description", "ADAS optics"),
        ("AI|DSC|Cabin", "DSC (cabin)"),
        ("AI|DSC|Lens Specification", "DSC lens"),
        ("AI|DSC|Description", "DSC optics"),
        ("AI|DMS|Configuration", "DMS"),
        ("AI|DMS|Lens Specification", "DMS lens"),
        ("AI|BSD Top View|Configuration", "BSD overhead"),
        ("AI|BSD Top View|Lens Specification", "BSD overhead camera"),
        ("AI|BSD Side View|Configuration", "BSD side"),
        ("AI|BSD Side View|Lens Specification", "BSD side camera"),
        ("AI|Combination|", "Max AI combination"),
        ("Optional Accessories|Rwatch|", "R-Watch"),
        ("Power Consumption|Maximum typical power consumption (without peripherals)|", "Power (bare)"),
        ("Power Consumption|Maximum typical power consumption (with full peripherals)|", "Power (loaded)"),
        ("Power Consumption|Standby power consumption|", "Power (standby)"),
        ("Operating Environment|Operating temperature|", "Operating temp"),
    ]
    for i, m in enumerate(models):
        add(f"### {m}")
        add("")
        add("| | |")
        add("|---|---|")
        for label, pretty in KEY:
            vals = by_key.get(label)
            if not vals:
                continue
            v = vals[i]
            if not v or v in ("/", "—"):
                continue
            add(f"| {pretty} | {md_escape(v)} |")
        add("")

    # ── differentiators ─────────────────────────────────────────────────────
    add("## Side by side — the fields deals actually turn on")
    add("")
    COMPARE = [
        ("Positioning", "Product Positioning||"),
        ("Status", "Product Status|Status|"),
        ("Video input", "Audio/Video|Video Input|"),
        ("Max resolution", "Audio/Video|Maximum Video Resolution|"),
        ("Storage", "Storage|Storage Medium/Maximum Capacity|"),
        ("Network", "Communication|Network Communication|"),
        ("CAN", "Interface|CAN|"),
        ("Max AI combination", "AI|Combination|"),
        ("Power (loaded)", "Power Consumption|Maximum typical power consumption (with full peripherals)|"),
    ]
    add("| Field | " + " | ".join(models) + " |")
    add("|---" * (len(models) + 1) + "|")
    for pretty, label in COMPARE:
        vals = row(label)
        add(f"| **{pretty}** | " + " | ".join(md_escape(v) or "—" for v in vals) + " |")
    add("")
    add(ANALYSIS)
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")
