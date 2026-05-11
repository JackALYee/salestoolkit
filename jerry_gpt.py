"""Jerry GPT — Streamlit-native chat module for the Sales Toolkit.

Lives at salestoolkit/jerry_gpt.py. Activated when the user clicks "Jerry GPT"
inside Streamaxpedia, which navigates to ?view=jerry_gpt. app.py then calls
render() instead of rendering the main toolkit HTML.

The Anthropic API key is read from st.secrets["ANTHROPIC_API_KEY"] first,
falling back to the ANTHROPIC_API_KEY environment variable.
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st


KNOWLEDGE_DIR = Path(__file__).parent / "jerry_gpt_knowledge"
ASSETS_DIR = Path(__file__).parent / "assets"
DEFAULT_MODEL = "claude-opus-4-7"


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

@st.cache_resource(show_spinner=False)
def _load_system_blocks() -> list[dict]:
    """Concatenate all knowledge files into one cacheable system-prompt block.

    Anthropic allows at most 4 cache_control breakpoints per request, so we
    combine the persona + 6 modules into a single block and mark it cacheable.
    """
    files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not files:
        return []
    sections = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        sections.append(f"<knowledge file=\"{path.name}\">\n{text}\n</knowledge>")
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

    /* Chat input */
    [data-testid="stChatInput"] {
        background: rgba(5, 8, 16, 0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(10px);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(42, 245, 152, 0.4) !important;
        box-shadow: 0 0 20px rgba(42, 245, 152, 0.15) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: var(--text-white) !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stChatInput"] button {
        color: var(--primary-green) !important;
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
# Public entry point
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Jerry GPT chat page. Called from app.py when view=jerry_gpt.

    Note: app.py has already called st.set_page_config(), so we do not call
    it again here (Streamlit raises if called twice in the same run).
    """
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    api_key = _get_api_key()
    model = _get_model()

    # --- Header ---
    st.markdown(
        f"""
        <div class="jerry-back-bar">
            <a href="/" target="_self" class="jerry-back-link">
                <i class="fa-solid fa-arrow-left"></i> Back to Toolkit
            </a>
        </div>
        <div class="jerry-header">
            <div class="jerry-subtitle">STREAMAX SALES TOOLKIT Extension - By Trucking BU</div>
            <h1 class="jerry-title">Jerry GPT</h1>
            <p class="jerry-tagline">Talk to Streamax's Product Marketing Director Jerry. Distilled by Jerry himself from 10 years at Streamax — so every customer conversation lands with a clearer, more convincing pitch.</p>
            <div class="jerry-meta">
                <span class="dot"></span>
                <span>{model}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- API key check ---
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
    if "jerry_gpt_history" not in st.session_state:
        st.session_state["jerry_gpt_history"] = []

    history: list[dict] = st.session_state["jerry_gpt_history"]

    # --- Welcome / quick prompts when empty ---
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
                _submit_message(prompt, system_blocks, api_key, model)
                st.rerun()

    # --- Render history ---
    for msg in history:
        with st.chat_message(msg["role"], avatar=JERRY_AVATAR if msg["role"] == "assistant" else USER_AVATAR):
            st.markdown(msg["content"])

    # --- Composer + actions ---
    col_a, col_b = st.columns([6, 1])
    with col_b:
        if st.button("🔄 New chat", use_container_width=True, disabled=not history):
            st.session_state["jerry_gpt_history"] = []
            st.rerun()

    user_input = st.chat_input("Ask Jerry anything…")
    if user_input:
        _submit_message(user_input, system_blocks, api_key, model)
        st.rerun()


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _submit_message(text: str, system_blocks: list[dict], api_key: str, model: str) -> None:
    """Append user turn, call Anthropic, append assistant turn. Streams to UI."""
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

    client = Anthropic(api_key=api_key)
    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]

    with st.chat_message("assistant", avatar=JERRY_AVATAR):
        placeholder = st.empty()
        full_text = ""

        try:
            with client.messages.stream(
                model=model,
                max_tokens=2048,
                system=system_blocks,
                messages=api_messages,
            ) as stream:
                for chunk in stream.text_stream:
                    full_text += chunk
                    placeholder.markdown(full_text + "▊")
            placeholder.markdown(full_text)
        except Exception as exc:
            history.pop()  # roll back user turn so retry works
            placeholder.markdown(
                f"<div class='jerry-error'><strong>API error.</strong><br>{type(exc).__name__}: {exc}</div>",
                unsafe_allow_html=True,
            )
            return

    history.append({"role": "assistant", "content": full_text})
