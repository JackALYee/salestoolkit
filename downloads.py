"""Downloadable-asset library for Jerry GPT.

When a user's topic matches a bundled file (today: eSIM → the Streamax eSIM
Solutions deck), Jerry's UI surfaces a download button beneath the answer.
Mirrors product_images.py: a small manifest + a keyword scanner.

Files live under assets/downloads/. find_downloads(text) returns metadata for
every asset whose trigger keywords appear in `text`; jerry_gpt.py renders an
st.download_button for each.
"""
from __future__ import annotations

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
]

MAX_DOWNLOADS = 3


def find_downloads(text: str) -> list[dict]:
    """Return [{id, path, filename, label, mime, blurb}, ...] for every asset
    whose trigger keywords appear in `text`. De-duped, capped, file-existence
    checked. Empty list if nothing matches."""
    if not text:
        return []
    low = text.lower()
    out: list[dict] = []
    seen: set[str] = set()
    for asset in ASSETS:
        if asset["id"] in seen:
            continue
        if any(kw in low for kw in asset["triggers"]):
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
    "When the user asks about eSIM, eUICC, MFF2, or SIM/connectivity for "
    "Streamax devices, a downloadable Streamax eSIM Solutions deck (PPTX) is "
    "available. Answer the question normally and mention 'eSIM' explicitly — "
    "the interface then automatically shows the user a download button for the "
    "deck. Do not paste links or invent a URL; just answer and name the topic."
)
