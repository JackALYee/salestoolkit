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
]

MAX_DOWNLOADS = 3

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
    "Two Streamax decks can be offered to the user as downloads:\n"
    "- eSIM: when the user asks about eSIM, eUICC, MFF2, or SIM/connectivity, "
    "mention 'eSIM' explicitly in your answer.\n"
    "- Inherent CAN: when the user asks about CAN bus, the CAN license, OBD/"
    "J1939 data, or reading vehicle data from the dashcam, mention 'CAN bus' "
    "explicitly in your answer.\n"
    "When you name the matching topic, the interface automatically shows the "
    "user a download button for that deck. Do not paste links or invent a URL "
    "— just answer the question and name the topic."
)
