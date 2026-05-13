"""Jerry GPT — Streamlit-native chat module for the Sales Toolkit.

Lives at salestoolkit/jerry_gpt.py. Activated when the user clicks "Jerry GPT"
inside Streamaxpedia, which navigates to ?view=jerry_gpt. app.py then calls
render() instead of rendering the main toolkit HTML.

The Anthropic API key is read from st.secrets["ANTHROPIC_API_KEY"] first,
falling back to the ANTHROPIC_API_KEY environment variable.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Usage logger — optional sibling module. Stdout always works; Google Sheets
# activates when secrets are configured. Never raises.
try:
    import usage_logger as _usage_logger
except Exception:
    _usage_logger = None


KNOWLEDGE_DIR = Path(__file__).parent / "jerry_gpt_knowledge"
ASSETS_DIR = Path(__file__).parent / "assets"
DEFAULT_MODEL = "claude-opus-4-7"

# --- Model catalog (display label -> Anthropic model id) ---
MODEL_OPTIONS = {
    "Opus 4.7 — highest quality": "claude-opus-4-7",
    "Sonnet 4.6 — balanced": "claude-sonnet-4-6",
    "Haiku 4.5 — fastest, cheapest": "claude-haiku-4-5-20251001",
}
MODEL_ID_TO_LABEL = {v: k for k, v in MODEL_OPTIONS.items()}

# --- Response length presets ---
# max_tokens caps the response; hint is appended to the user message so Jerry
# adjusts his structure (concise reply vs. full structured breakdown).
LENGTH_OPTIONS = {
    "Short": {
        "max_tokens": 512,
        "hint": "Keep this response tight — 1-2 short paragraphs, no headers, no tables. Just the punch line and the why.",
    },
    "Medium": {
        "max_tokens": 1536,
        "hint": "",  # default, no extra instruction
    },
    "Long": {
        "max_tokens": 4096,
        "hint": "Take the space to be thorough. Use headers, comparative tables, and structured frameworks where they help.",
    },
}

EMPTY_USAGE = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read_tokens": 0,
    "cache_creation_tokens": 0,
    "message_count": 0,
}


def _find_jerry_avatar() -> str:
    """Return absolute path to Jerry's portrait if found, else fallback emoji.

    st.chat_message(avatar=...) accepts either an emoji or a file path.
    Streamlit renders the avatar inside a ~36px circular frame and auto-
    crops/scales the image, so no resizing is needed in code — we just
    point to the file. Falls back to 🤖 if the portrait isn't present.
    """
    for name in ("jerry.png", "jerry.jpg", "jerry.jpeg", "jerry.webp"):
        path = ASSETS_DIR / name
        if path.is_file():
            return str(path)
    return "🤖"


JERRY_AVATAR = _find_jerry_avatar()
USER_AVATAR = "🧑"


# ---------------------------------------------------------------------------
# Knowledge loading (cached across reruns)
# ---------------------------------------------------------------------------

def _generate_streamaxpedia_knowledge() -> str:
    """Build a markdown section from terminology_db.py at module load.

    Pulls in every product term, description, related products, file URLs,
    and the validated product architectures. Jerry gets a full Streamaxpedia
    snapshot inside his system prompt — so he knows every SKU, what it does,
    what it pairs with, and where to find the spec sheet.
    """
    try:
        from terminology_db import TERMINOLOGY_DB, PRODUCT_COMBINATIONS
    except Exception:
        return ""

    lines: list[str] = []
    lines.append("# Streamaxpedia — Product Database & Architectures")
    lines.append("")
    lines.append(
        "This section is generated from the Streamaxpedia database "
        "(`terminology_db.py`). It contains every Streamax product term, "
        "category, short description, related products, and downloadable "
        "spec-sheet / user-manual URLs. When a user asks where to download "
        "documentation for a product, give them the exact URL from this list. "
        "When asked which architecture supports a given capability (DMS, ADAS, "
        "DSC, BSIS, BSD, AVM, channel count, on-device storage), use the "
        "Validated Product Architectures table below — these are the official "
        "Streamax-approved compositions."
    )
    lines.append("")

    # --- Group terminology by category ---
    by_category: dict[str, list[dict]] = {}
    for entry in TERMINOLOGY_DB:
        cat = (entry.get("category") or "OTHER").upper()
        by_category.setdefault(cat, []).append(entry)

    lines.append("## Product & Technology Catalog")
    for cat in sorted(by_category.keys()):
        lines.append(f"\n### {cat}")
        for entry in by_category[cat]:
            term = entry.get("term", "").strip()
            desc = (entry.get("desc") or "").strip()
            related = entry.get("related") or []
            files = entry.get("files") or []
            if not term:
                continue
            lines.append(f"\n**{term}**")
            if desc:
                lines.append(f"- {desc}")
            if related:
                lines.append(f"- Related: {', '.join(related)}")
            for f in files:
                label = (f.get("label") or "Download").strip()
                url = (f.get("url") or "").strip()
                if url:
                    lines.append(f"- {label}: {url}")

    # --- Validated product architectures ---
    if PRODUCT_COMBINATIONS:
        lines.append("\n## Validated Product Architectures")
        lines.append("")
        lines.append(
            "Each row is an officially validated Streamax product combination — "
            "the AI capability tier, monitoring channel count, on-device storage, "
            "the product composition (architecture formula), and which safety "
            "features that combination supports."
        )
        lines.append("")
        lines.append("| AI tier | Channels | Storage | Composition | DMS | ADAS | DSC | BSIS | BSD | AVM |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for combo in PRODUCT_COMBINATIONS:
            row = "| {ai} | {ch} | {hdd} | {comp} | {dms} | {adas} | {dsc} | {bsis} | {bsd} | {avm} |".format(
                ai=combo.get("ai", "").strip() or "—",
                ch=combo.get("ch", "").strip() or "—",
                hdd=combo.get("hdd", "").strip() or "—",
                comp=(combo.get("composition") or "").strip().replace("|", "/") or "—",
                dms=combo.get("dms", "").strip() or "—",
                adas=combo.get("adas", "").strip() or "—",
                dsc=combo.get("dsc", "").strip() or "—",
                bsis=combo.get("bsis", "").strip() or "—",
                bsd=combo.get("bsd", "").strip() or "—",
                avm=combo.get("avm", "").strip() or "—",
            )
            lines.append(row)

    return "\n".join(lines)


@st.cache_resource(show_spinner=False)
def _load_system_blocks() -> list[dict]:
    """Concatenate all knowledge sources into one cacheable system-prompt block.

    Sources, in order:
      1. Hand-curated persona + 6 topical modules in jerry_gpt_knowledge/
      2. Generated Streamaxpedia snapshot (terminology + architectures)

    Anthropic allows at most 4 cache_control breakpoints per request, so we
    combine everything into a single ephemeral-cached block.
    """
    files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not files:
        return []
    sections = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        sections.append(f"<knowledge file=\"{path.name}\">\n{text}\n</knowledge>")

    spedia = _generate_streamaxpedia_knowledge()
    if spedia:
        sections.append(f"<knowledge file=\"streamaxpedia_generated.md\">\n{spedia}\n</knowledge>")

    combined = "\n\n".join(sections)
    return [
        {
            "type": "text",
            "text": combined,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _get_api_key() -> str | None:
    """Look up the Anthropic API key in st.secrets, then env vars."""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def _get_model() -> str:
    try:
        m = st.secrets.get("JERRY_MODEL")
        if m:
            return m
    except Exception:
        pass
    return os.environ.get("JERRY_MODEL", DEFAULT_MODEL)


# ---------------------------------------------------------------------------
# Theme — matches the salestoolkit dark Streamax design system
# ---------------------------------------------------------------------------

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    :root {
        --bg-deep: #050810;
        --primary-green: #2AF598;
        --secondary-blue: #009EFD;
        --text-white: #FFFFFF;
        --text-grey: #A0AEC0;
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: 1px solid rgba(255, 255, 255, 0.08);
        --gradient-text: linear-gradient(135deg, #2AF598 0%, #009EFD 100%);
    }

    /* App-wide background + grid overlay */
    .stApp {
        background-color: var(--bg-deep) !important;
        background-image: radial-gradient(circle at 50% -20%, #0B1221, #050810) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-white) !important;
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        opacity: 0.05;
        z-index: 0;
        pointer-events: none;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
    .stDeployButton { display: none; }

    /* --- Bulletproof input dark mode --------------------------------------
       Survives: Chrome/Safari autofill (which repaints fields white/yellow),
       OS-level dark-mode color-scheme inheritance, Streamlit DOM changes,
       and any browser default that would otherwise flip backgrounds light. */
    .stApp input,
    .stApp textarea {
        color-scheme: dark !important;
        background-color: rgba(20, 25, 40, 0.6) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #2AF598 !important;
    }
    .stApp input::placeholder,
    .stApp textarea::placeholder {
        color: rgba(160, 174, 192, 0.55) !important;
        -webkit-text-fill-color: rgba(160, 174, 192, 0.55) !important;
        opacity: 1 !important;
    }
    /* Defeat Chrome/Safari autofill yellow/white repaint */
    .stApp input:-webkit-autofill,
    .stApp input:-webkit-autofill:hover,
    .stApp input:-webkit-autofill:focus,
    .stApp input:-webkit-autofill:active,
    .stApp textarea:-webkit-autofill,
    .stApp textarea:-webkit-autofill:focus {
        -webkit-text-fill-color: #ffffff !important;
        -webkit-box-shadow: 0 0 0 1000px rgba(20, 25, 40, 0.95) inset !important;
        caret-color: #2AF598 !important;
        transition: background-color 5000s ease-in-out 0s;
    }

    .block-container {
        max-width: 1080px !important;
        padding-top: 2rem !important;
        padding-bottom: 8rem !important;
        position: relative;
        z-index: 1;
    }

    /* Header */
    .jerry-header { text-align: center; padding: 16px 0 24px; }
    .jerry-subtitle {
        font-size: 0.75rem; text-transform: uppercase; letter-spacing: 3px;
        color: var(--primary-green); margin-bottom: 12px; font-weight: 600;
    }
    .jerry-title {
        font-size: 2.8rem; font-weight: 800; letter-spacing: -1px;
        background: var(--gradient-text);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        margin-bottom: 12px; line-height: 1.1;
    }
    .jerry-tagline {
        color: var(--text-grey) !important;
        max-width: 680px !important;
        width: auto !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-top: 0 !important;
        margin-bottom: 16px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        text-align: center !important;
        display: block !important;
    }
    .jerry-meta {
        display: inline-flex; align-items: center; gap: 10px;
        padding: 6px 14px;
        background: var(--glass-bg); border: var(--glass-border); border-radius: 30px;
        backdrop-filter: blur(8px);
        font-size: 0.78rem; color: var(--text-grey);
    }
    .jerry-meta .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--primary-green);
        box-shadow: 0 0 6px var(--primary-green);
        animation: jerryPulse 2s ease-in-out infinite;
    }
    @keyframes jerryPulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

    /* Back link */
    .jerry-back-bar { margin: 12px 0 24px; }
    .jerry-back-link {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 14px; border-radius: 8px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--text-grey); text-decoration: none;
        font-size: 0.85rem; font-weight: 500;
        transition: all 0.2s;
    }
    .jerry-back-link:hover {
        border-color: var(--primary-green);
        color: var(--primary-green);
        background: rgba(42, 245, 152, 0.05);
    }

    /* Chat message bubbles */
    [data-testid="stChatMessage"] {
        background: var(--glass-bg) !important;
        border: var(--glass-border) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 14px !important;
        backdrop-filter: blur(12px);
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: var(--text-white) !important;
    }
    [data-testid="stChatMessage"] strong { color: var(--text-white) !important; }
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3 { color: var(--text-white) !important; }
    [data-testid="stChatMessage"] h3 {
        color: var(--primary-green) !important;
        text-transform: uppercase; letter-spacing: 1.5px;
        font-size: 0.85rem;
    }
    [data-testid="stChatMessage"] code {
        background: rgba(0,0,0,0.35) !important;
        color: var(--primary-green) !important;
        padding: 2px 6px !important; border-radius: 4px !important;
        font-size: 0.85em !important;
    }
    [data-testid="stChatMessage"] blockquote {
        border-left: 3px solid var(--secondary-blue) !important;
        background: rgba(0, 158, 253, 0.06) !important;
        padding: 10px 16px !important;
        border-radius: 0 8px 8px 0;
    }
    [data-testid="stChatMessage"] table { background: rgba(0,0,0,0.2); }
    [data-testid="stChatMessage"] th {
        background: rgba(42, 245, 152, 0.06) !important;
        color: var(--primary-green) !important;
        text-transform: uppercase; letter-spacing: 1px;
        font-size: 0.78rem;
    }
    [data-testid="stChatMessage"] td { color: var(--text-grey) !important; }

    /* Assistant avatar — shows Jerry's portrait inside a gradient ring */
    [data-testid="stChatMessageAvatarAssistant"] {
        background: var(--gradient-text) !important;
        color: #050810 !important;
        padding: 2px !important;
        box-shadow: 0 0 12px rgba(42, 245, 152, 0.25) !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] img {
        border-radius: 50% !important;
        object-fit: cover !important;
        width: 100% !important;
        height: 100% !important;
        border: 2px solid #050810 !important;
        background: #050810 !important;
    }

    /* Chat input — paint EVERY wrapper layer dark so no white wrapper shows
       through (Windows Edge + High Contrast + BaseWeb wrappers all defeat the
       single-selector approach). */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="base-input"],
    [data-testid="stChatInputContainer"],
    [data-testid="stChatInputTextArea"] {
        background: rgba(5, 8, 16, 0.85) !important;
        background-color: rgba(5, 8, 16, 0.85) !important;
        background-image: none !important;
        color-scheme: dark !important;
        forced-color-adjust: none !important;
    }
    [data-testid="stChatInput"] {
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(10px);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(42, 245, 152, 0.4) !important;
        box-shadow: 0 0 20px rgba(42, 245, 152, 0.15) !important;
    }
    /* Textarea itself: transparent, so the dark wrapper shows through */
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #2AF598 !important;
        font-family: 'Inter', sans-serif !important;
        color-scheme: dark !important;
        forced-color-adjust: none !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: rgba(160, 174, 192, 0.55) !important;
        -webkit-text-fill-color: rgba(160, 174, 192, 0.55) !important;
        opacity: 1 !important;
    }
    [data-testid="stChatInput"] button {
        color: var(--primary-green) !important;
        forced-color-adjust: none !important;
    }

    /* Quick prompt buttons */
    .quick-prompts { display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0 20px; }
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-grey) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 8px 14px !important;
        border-radius: 10px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: rgba(42, 245, 152, 0.06) !important;
        border-color: rgba(42, 245, 152, 0.35) !important;
        color: var(--text-white) !important;
        transform: translateY(-1px);
    }

    /* Welcome empty state */
    .jerry-welcome {
        text-align: center;
        padding: 36px 24px;
        background: var(--glass-bg);
        border: var(--glass-border);
        border-radius: 16px;
        margin: 20px 0 24px;
    }
    .jerry-welcome-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 5px 12px;
        background: rgba(42, 245, 152, 0.08);
        border: 1px solid rgba(42, 245, 152, 0.25);
        border-radius: 30px;
        color: var(--primary-green);
        font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2px;
        margin-bottom: 14px;
    }
    .jerry-welcome h2 {
        font-size: 1.6rem; font-weight: 700; color: var(--text-white);
        margin-bottom: 10px;
    }
    .jerry-welcome p {
        color: var(--text-grey); font-size: 0.92rem; max-width: 560px;
        margin: 0 auto; line-height: 1.6;
    }

    /* Side panel (settings + stats) */
    .jerry-side-card {
        background: var(--glass-bg);
        border: var(--glass-border);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
    }
    .jerry-side-title {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--primary-green);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .jerry-side-title i { font-size: 0.8rem; }

    .jerry-stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        color: var(--text-grey);
        padding: 6px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .jerry-stat-row:last-of-type { border-bottom: none; }
    .jerry-stat-row .val {
        color: var(--text-white);
        font-weight: 600;
        font-variant-numeric: tabular-nums;
        font-family: 'Roboto Mono', 'SF Mono', Menlo, monospace;
    }
    .jerry-stat-hint {
        font-size: 0.65rem;
        color: var(--text-grey);
        opacity: 0.6;
        margin-top: 8px;
        line-height: 1.4;
    }

    /* Streamlit widget overrides inside the side card */
    .jerry-side-card .stSelectbox label,
    .jerry-side-card .stRadio label {
        font-size: 0.72rem !important;
        color: var(--text-grey) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Copy-markdown button (per Jerry response) */
    .jerry-copy-row {
        display: flex;
        justify-content: flex-end;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    .jerry-copy-btn {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: var(--text-grey);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: inherit;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
        letter-spacing: 0.3px;
    }
    .jerry-copy-btn i { font-size: 0.7rem; }
    .jerry-copy-btn:hover {
        border-color: var(--primary-green);
        color: var(--primary-green);
        background: rgba(42, 245, 152, 0.05);
    }
    .jerry-copy-btn.copied {
        border-color: var(--primary-green);
        color: var(--primary-green);
        background: rgba(42, 245, 152, 0.12);
    }

    /* Error / config panels */
    .jerry-error {
        padding: 20px 24px;
        background: rgba(248, 113, 113, 0.06);
        border-left: 3px solid #f87171;
        border-radius: 0 10px 10px 0;
        color: #fecaca;
        margin: 16px 0;
    }
    .jerry-error code {
        background: rgba(0,0,0,0.4); padding: 2px 6px;
        border-radius: 4px; color: var(--primary-green);
    }
</style>
"""


QUICK_PROMPTS = [
    ("📣 60-second TSP pitch", "Give me the 60-second TSP pitch."),
    ("🎯 vs. Motive in NA", "How do I position Streamax against Motive in North America?"),
    ("👤 Drivers won't accept", "A fleet manager says drivers won't accept cameras. How do I respond?"),
    ("👁️ DSC vs DMS", "Walk me through the DSC vs DMS argument for fatigue detection."),
    ("🇮🇳 India strategy", "What's the strategy for entering India?"),
    ("🔄 Data flywheel", "Explain the data flywheel and why it matters."),
]


# ---------------------------------------------------------------------------
# Copy-to-clipboard button (rendered under each Jerry response)
# ---------------------------------------------------------------------------

_COPY_BUTTON_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  html, body { margin: 0; padding: 0; background: transparent; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #A0AEC0;
  }
  .row { display: flex; justify-content: flex-end; padding: 4px 0; }
  .btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #A0AEC0;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s;
    letter-spacing: 0.3px;
  }
  .btn i { font-size: 0.7rem; }
  .btn:hover {
    border-color: #2AF598;
    color: #2AF598;
    background: rgba(42, 245, 152, 0.06);
  }
  .btn.copied {
    border-color: #2AF598;
    color: #2AF598;
    background: rgba(42, 245, 152, 0.14);
  }
</style>
</head>
<body>
<div class="row">
  <button class="btn" type="button" id="b">
    <i class="fa-solid fa-copy"></i><span id="lbl">Copy markdown</span>
  </button>
</div>
<script>
  (function() {
    var b64 = "__B64__";
    var btn = document.getElementById("b");
    var lbl = document.getElementById("lbl");

    function decode() {
      var binary = atob(b64);
      var bytes = new Uint8Array(binary.length);
      for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      return new TextDecoder("utf-8").decode(bytes);
    }

    function flash() {
      btn.classList.add("copied");
      var original = lbl.textContent;
      lbl.textContent = "Copied";
      setTimeout(function() {
        btn.classList.remove("copied");
        lbl.textContent = original;
      }, 1500);
    }

    function fallbackCopy(text) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "0";
      ta.style.left = "0";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      return ok;
    }

    btn.addEventListener("click", function() {
      var text = decode();
      if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(flash).catch(function() {
          if (fallbackCopy(text)) flash();
        });
      } else {
        if (fallbackCopy(text)) flash();
      }
    });
  })();
</script>
</body>
</html>
"""


def _render_copy_button(text: str) -> None:
    """Render a 'Copy markdown' button beneath an assistant message.

    Uses st.components.v1.html() so the click handler actually runs —
    st.markdown() strips inline event handlers in newer Streamlit versions.
    The iframe is height=42, just tall enough for the button row.

    Text is base64-encoded so it embeds safely in the inline JS regardless
    of quotes, newlines, em-dashes, or unicode content (Chinese, emoji).
    Tries the modern Clipboard API first, falls back to a hidden-textarea
    + document.execCommand('copy') for older browsers and iframe contexts
    where the Clipboard API is blocked.
    """
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    components.html(
        _COPY_BUTTON_HTML.replace("__B64__", b64),
        height=42,
        scrolling=False,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    """Create all the Jerry-GPT keys in session_state if missing."""
    if "jerry_gpt_history" not in st.session_state:
        st.session_state["jerry_gpt_history"] = []
    if "jerry_gpt_model" not in st.session_state:
        st.session_state["jerry_gpt_model"] = _get_model()
    if "jerry_gpt_length" not in st.session_state:
        st.session_state["jerry_gpt_length"] = "Medium"
    if "jerry_gpt_usage" not in st.session_state:
        st.session_state["jerry_gpt_usage"] = dict(EMPTY_USAGE)


def _render_side_panel() -> None:
    """Right column: model selector, response length, cumulative stats."""
    # --- Settings card ---
    st.markdown(
        '<div class="jerry-side-card"><div class="jerry-side-title">'
        '<i class="fa-solid fa-sliders"></i><span>Settings</span></div>',
        unsafe_allow_html=True,
    )

    # Model selector — preserves choice across reruns via session_state key
    current_model = st.session_state.get("jerry_gpt_model", DEFAULT_MODEL)
    current_label = MODEL_ID_TO_LABEL.get(current_model, list(MODEL_OPTIONS.keys())[0])
    model_labels = list(MODEL_OPTIONS.keys())
    selected_label = st.selectbox(
        "Model",
        model_labels,
        index=model_labels.index(current_label),
        key="jerry_model_selectbox",
    )
    st.session_state["jerry_gpt_model"] = MODEL_OPTIONS[selected_label]

    # Length selector
    length_keys = list(LENGTH_OPTIONS.keys())
    current_length = st.session_state.get("jerry_gpt_length", "Medium")
    selected_length = st.radio(
        "Response length",
        length_keys,
        index=length_keys.index(current_length),
        key="jerry_length_radio",
        horizontal=True,
    )
    st.session_state["jerry_gpt_length"] = selected_length

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Stats card ---
    usage = st.session_state["jerry_gpt_usage"]
    total_tokens = (
        usage["input_tokens"]
        + usage["output_tokens"]
        + usage["cache_read_tokens"]
        + usage["cache_creation_tokens"]
    )
    st.markdown(
        f"""
        <div class="jerry-side-card">
          <div class="jerry-side-title">
            <i class="fa-solid fa-chart-line"></i><span>Session usage</span>
          </div>
          <div class="jerry-stat-row"><span>Messages</span><span class="val">{usage['message_count']}</span></div>
          <div class="jerry-stat-row"><span>Input tokens</span><span class="val">{usage['input_tokens']:,}</span></div>
          <div class="jerry-stat-row"><span>Output tokens</span><span class="val">{usage['output_tokens']:,}</span></div>
          <div class="jerry-stat-row"><span>Cache reads</span><span class="val">{usage['cache_read_tokens']:,}</span></div>
          <div class="jerry-stat-row"><span>Cache writes</span><span class="val">{usage['cache_creation_tokens']:,}</span></div>
          <div class="jerry-stat-row"><span>Total tokens</span><span class="val">{total_tokens:,}</span></div>
          <div class="jerry-stat-hint">Cache reads represent prompt-cache hits — the knowledge base loads once per model, then most input tokens come from cache on follow-up turns.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Reset stats", use_container_width=True, key="reset_stats_btn"):
        st.session_state["jerry_gpt_usage"] = dict(EMPTY_USAGE)
        st.rerun()


def _update_usage(model_id: str, usage_obj) -> None:
    """Add this turn's token counts to the session-cumulative stats."""
    stats = st.session_state["jerry_gpt_usage"]
    stats["input_tokens"] += getattr(usage_obj, "input_tokens", 0) or 0
    stats["output_tokens"] += getattr(usage_obj, "output_tokens", 0) or 0
    stats["cache_read_tokens"] += getattr(usage_obj, "cache_read_input_tokens", 0) or 0
    stats["cache_creation_tokens"] += getattr(usage_obj, "cache_creation_input_tokens", 0) or 0
    stats["message_count"] += 1


def render() -> None:
    """Render the Jerry GPT chat page. Called from app.py when view=jerry_gpt.

    Note: app.py has already called st.set_page_config(), so we do not call
    it again here (Streamlit raises if called twice in the same run).
    """
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    api_key = _get_api_key()

    # --- API key check (fail early, before initing state we don't need) ---
    if not api_key:
        st.markdown(
            """
            <div class="jerry-error">
                <strong>Anthropic API key missing.</strong><br><br>
                Add <code>ANTHROPIC_API_KEY</code> to <code>.streamlit/secrets.toml</code>
                (locally) or to your Streamlit Cloud app secrets:
                <pre style="background:rgba(0,0,0,0.4); padding:12px; border-radius:6px; margin-top:10px;">
ANTHROPIC_API_KEY = "sk-ant-..."
JERRY_MODEL = "claude-opus-4-7"</pre>
                Then refresh this page.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    # --- Knowledge check ---
    system_blocks = _load_system_blocks()
    if not system_blocks:
        st.markdown(
            f"""
            <div class="jerry-error">
                <strong>Knowledge base not found.</strong><br><br>
                Expected markdown files under <code>{KNOWLEDGE_DIR}</code>.
                Make sure the <code>jerry_gpt_knowledge/</code> folder is committed
                alongside <code>jerry_gpt.py</code>.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    # --- Session state ---
    _init_session_state()
    history: list[dict] = st.session_state["jerry_gpt_history"]
    model = st.session_state["jerry_gpt_model"]
    length = st.session_state["jerry_gpt_length"]

    # --- Header (full width) ---
    st.markdown(
        f"""
        <div class="jerry-back-bar">
            <a href="/" target="_self" class="jerry-back-link">
                <i class="fa-solid fa-arrow-left"></i> Back to Toolkit
            </a>
        </div>
        <div class="jerry-header">
            <div class="jerry-subtitle">A STREAMAX SALES TOOLKIT Extension - By Trucking BU</div>
            <h1 class="jerry-title">Jerry GPT</h1>
            <p class="jerry-tagline">Talk to Streamax's Product Marketing Director Jerry. Distilled by Jerry himself from 10 years at Streamax — so every customer conversation lands with a clearer, more convincing pitch.</p>
            <div class="jerry-meta">
                <span class="dot"></span>
                <span>{MODEL_ID_TO_LABEL.get(model, model)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Two-column body: main chat + side panel ---
    col_main, col_side = st.columns([3, 1], gap="large")

    with col_side:
        _render_side_panel()

    with col_main:
        # Welcome + quick prompts when empty
        if not history:
            st.markdown(
                """
                <div class="jerry-welcome">
                    <div class="jerry-welcome-badge">
                        <i class="fa-solid fa-comments"></i> READY TO TALK
                    </div>
                    <h2>What would Jerry say?</h2>
                    <p>Ask about positioning, the competitive landscape, regional strategy, product portfolio, objection handling, or any conversation you're prepping for. Jerry leads with outcomes, sources, and structured frameworks.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            cols = st.columns(3)
            for i, (label, prompt) in enumerate(QUICK_PROMPTS):
                if cols[i % 3].button(label, key=f"qp_{i}", use_container_width=True):
                    _submit_message(prompt, system_blocks, api_key, model, length)
                    st.rerun()

        # Chat history
        for msg in history:
            with st.chat_message(msg["role"], avatar=JERRY_AVATAR if msg["role"] == "assistant" else USER_AVATAR):
                st.markdown(msg["content"])
                if msg["role"] == "assistant":
                    _render_copy_button(msg["content"])

        # New-chat button row
        _col_a, _col_b = st.columns([6, 1])
        with _col_b:
            if st.button("🔄 New chat", use_container_width=True, disabled=not history, key="new_chat_btn"):
                st.session_state["jerry_gpt_history"] = []
                st.rerun()

        # Chat input (renders inline at bottom of col_main)
        user_input = st.chat_input("Ask Jerry anything…")
        if user_input:
            _submit_message(user_input, system_blocks, api_key, model, length)
            st.rerun()


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _submit_message(
    text: str,
    system_blocks: list[dict],
    api_key: str,
    model: str,
    length: str = "Medium",
) -> None:
    """Append user turn, call Anthropic, append assistant turn. Streams to UI.

    `length` is one of LENGTH_OPTIONS keys (Short / Medium / Long) — controls
    both max_tokens and an instruction appended to the user message that
    nudges Jerry's response structure.
    """
    history: list[dict] = st.session_state["jerry_gpt_history"]
    history.append({"role": "user", "content": text})

    # Render user turn immediately so it appears during streaming
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(text)

    try:
        from anthropic import Anthropic
    except ImportError:
        history.pop()  # roll back user turn
        st.error(
            "The `anthropic` package isn't installed. Run `pip install anthropic` "
            "(or update requirements.txt and redeploy)."
        )
        return

    length_cfg = LENGTH_OPTIONS.get(length, LENGTH_OPTIONS["Medium"])
    max_tokens = length_cfg["max_tokens"]
    hint = length_cfg["hint"]

    client = Anthropic(api_key=api_key)
    # Build API messages from history. If the user has selected a short or long
    # response, append the length hint to the LATEST user message so Jerry
    # adjusts structure — but don't mutate the stored history (so the hint
    # doesn't accumulate across turns or appear in the UI).
    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]
    if hint and api_messages and api_messages[-1]["role"] == "user":
        api_messages[-1] = {
            "role": "user",
            "content": api_messages[-1]["content"] + f"\n\n[Length preference: {hint}]",
        }

    with st.chat_message("assistant", avatar=JERRY_AVATAR):
        placeholder = st.empty()
        full_text = ""

        try:
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=system_blocks,
                messages=api_messages,
            ) as stream:
                for chunk in stream.text_stream:
                    full_text += chunk
                    placeholder.markdown(full_text + "▊")
                final_message = stream.get_final_message()
            placeholder.markdown(full_text)
            _render_copy_button(full_text)
            # Track cumulative token stats for the side panel
            _update_usage(model, final_message.usage)
            # Append this turn to the usage log (stdout + optional Google Sheets)
            if _usage_logger is not None:
                usage_obj = final_message.usage
                _usage_logger.log_query(
                    question=text,
                    model=model,
                    length=length,
                    input_tokens=getattr(usage_obj, "input_tokens", 0) or 0,
                    output_tokens=getattr(usage_obj, "output_tokens", 0) or 0,
                    cache_read_tokens=getattr(usage_obj, "cache_read_input_tokens", 0) or 0,
                    cache_creation_tokens=getattr(usage_obj, "cache_creation_input_tokens", 0) or 0,
                )
        except Exception as exc:
            history.pop()  # roll back user turn so retry works
            placeholder.markdown(
                f"<div class='jerry-error'><strong>API error.</strong><br>{type(exc).__name__}: {exc}</div>",
                unsafe_allow_html=True,
            )
            return

    history.append({"role": "assistant", "content": full_text})
