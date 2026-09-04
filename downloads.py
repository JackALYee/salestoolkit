"""Downloadable-asset library for Jerry GPT.

When a user's topic matches a bundled file (today: eSIM → the Streamax eSIM
Solutions deck), Jerry's UI surfaces a download button beneath the answer.
Mirrors product_images.py: a small manifest + a keyword scanner.

Files live under assets/downloads/. find_downloads(text) returns metadata for
every asset whose trigger keywords appear in `text`; jerry_gpt.py renders an
st.download_button for each.
"""
from __future__ import annotations

import re
from pathlib import Path

_DOWNLOADS_DIR = Path(__file__).parent / "assets" / "downloads"

# Each asset: trigger keywords (matched case-insensitively as substrings —
# keep them distinctive so they don't fire on unrelated words), plus the file
# + how to present it. Avoid generic tokens like "sim" (matches "similar").
ASSETS = [
    {
        "id": "esim_deck",
        "triggers": ["esim", "e-sim", "euicc", "mff2"],
        "filename": "Streamax-eSIM-Solutions-v2.pptx",
        "label": "Download · Streamax eSIM Solutions (PPTX)",
        "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "blurb": "The full Streamax eSIM Solutions deck — pain points, form factors, value props, TCO, and data-plan pooling.",
    },
    {
        "id": "can_deck",
        # Distinctive multi-char tokens only — never bare "can" (the English word).
        "triggers": ["can bus", "canbus", "can-bus", "inherent can",
                     "can license", "j1939", "obd"],
        "filename": "Streamax Inherent CAN — Partner Enablement.pptx",
        "label": "Download · Streamax Inherent CAN — Partner Enablement (PPTX)",
        "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "blurb": "The full Inherent CAN partner-enablement deck — the $20 license vs. $60 tracker economics, 24+ parameters, 3,000+ vehicle coverage, and FT Cloud activation.",
    },
    # ── GDPR set ────────────────────────────────────────────────────────────
    # Deliberately NOT triggered by a bare "gdpr": Jerry discusses GDPR in
    # almost any EU compliance answer, and attaching three files to every one
    # of them is noise. Each deck fires on the phrases specific to its own
    # subject instead.
    {
        "id": "gdpr_data_boundary_deck",
        "triggers": ["privacy by design", "data boundary", "masking",
                     "mosaic", "privacy masking", "geofence recording",
                     "alert tolerance", "tiered retention", "打码", "数据边界"],
        "filename": "Streamax-GDPR-Data-Boundary-Slides.zip",
        "label": "Download · GDPR Data-Boundary deck, 10 slides (ZIP, open 点击播放.html)",
        "mime": "application/zip",
        "blurb": "The five privacy features mapped to GDPR articles — masking, alert tolerance, geofence auto-stop, event-only upload, tiered retention. Product-function material, not legal advice.",
    },
    {
        "id": "gdpr_roles_deck",
        "triggers": ["controller", "processor", "dpa", "data processing agreement",
                     "dpia", "ropa", "legitimate interests", "works council",
                     "betriebsvereinbarung", "article 28", "art. 28",
                     "分清角色", "四件套"],
        "filename": "Streamax-GDPR-Roles-and-Contracting-Slides.zip",
        "label": "Download · GDPR Roles & Contracting deck, 8 slides (ZIP, open 点击播放.html)",
        "mime": "application/zip",
        "blurb": "Controller vs Processor, the DPA/LIA/DPIA/ROPA four-piece set and who signs each, DMS design red lines, and the two-layer in-vehicle notice. INTERNAL — do not forward outside Streamax.",
    },
    {
        "id": "gdpr_regulatory_briefing",
        "triggers": ["cra", "cyber resilience act", "eu ai act", "nis2",
                     "itxpt", "vdv 301", "ibis-ip", "sccs", "scc + tia",
                     "transfer impact assessment", "cross-border transfer",
                     "adequacy decision", "article 44", "regulatory landscape",
                     "跨境传输", "法规全景"],
        "filename": "Streamax-GDPR-EU-Regulatory-Briefing.pdf",
        "label": "Download · EU Regulatory Landscape & GDPR Briefing (PDF, 7 pages)",
        "mime": "application/pdf",
        "blurb": "The full EU matrix — GDPR, CRA, AI Act, NIS2, RED, GSR, CE, ITxPT, VDV 301 — plus role definition, Art. 9 triggers, DPA clauses, SCC+TIA for China transfers, and enforcement precedents. INTERNAL.",
    },
]

# Three GDPR assets can plausibly match one compliance answer, so the cap has
# to clear that or the third is silently dropped.
MAX_DOWNLOADS = 4

# Pre-compile a word-boundary regex per asset so triggers match as whole
# tokens — "obd" fires on "OBD-II" but NOT inside "obdurate", and bare "can"
# is never a trigger so the English word "can" can't false-match.
_ASSET_PATTERNS = {
    asset["id"]: re.compile(
        r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(kw) for kw in asset["triggers"]) + r")(?![A-Za-z0-9])",
        re.IGNORECASE,
    )
    for asset in ASSETS
}


def find_downloads(text: str) -> list[dict]:
    """Return [{id, path, filename, label, mime, blurb}, ...] for every asset
    whose trigger keywords appear in `text` as whole tokens. De-duped, capped,
    file-existence checked. Empty list if nothing matches."""
    if not text:
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for asset in ASSETS:
        if asset["id"] in seen:
            continue
        if _ASSET_PATTERNS[asset["id"]].search(text):
            path = _DOWNLOADS_DIR / asset["filename"]
            if path.is_file():
                out.append({
                    "id": asset["id"],
                    "path": str(path),
                    "filename": asset["filename"],
                    "label": asset["label"],
                    "mime": asset["mime"],
                    "blurb": asset["blurb"],
                })
                seen.add(asset["id"])
        if len(out) >= MAX_DOWNLOADS:
            break
    return out


# Injected into Jerry's system prompt so he names the topic (which is what
# lets the scanner attach the file) and knows the download exists.
DOWNLOAD_HINT = (
    "Five Streamax documents can be offered to the user as downloads:\n"
    "- eSIM: when the user asks about eSIM, eUICC, MFF2, or SIM/connectivity, "
    "mention 'eSIM' explicitly in your answer.\n"
    "- Inherent CAN: when the user asks about CAN bus, the CAN license, OBD/"
    "J1939 data, or reading vehicle data from the dashcam, mention 'CAN bus' "
    "explicitly in your answer.\n"
    "- GDPR Data-Boundary deck (10 slides): for questions about the privacy "
    "features themselves — name 'privacy masking', 'alert tolerance', "
    "'geofence recording' or 'tiered retention'.\n"
    "- GDPR Roles & Contracting deck (8 slides): for who signs what — name "
    "'controller', 'processor', 'DPA', 'DPIA' or 'works council'.\n"
    "- EU Regulatory Landscape & GDPR briefing (7-page PDF): for the wider "
    "regulatory picture or China transfers — name 'CRA', 'EU AI Act', 'NIS2', "
    "or 'cross-border transfer'.\n"
    "When you name the matching topic the interface attaches the download "
    "button automatically. Do not paste links or invent a URL — answer the "
    "question and name the topic.\n"
    "The two GDPR decks and the briefing are INTERNAL Streamax material. When "
    "you offer one, say it is for internal use and should not be forwarded to "
    "a customer. The GDPR whitepaper is a legal-review draft and is "
    "deliberately NOT downloadable — never offer it."
)
