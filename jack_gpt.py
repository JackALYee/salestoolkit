"""Jack GPT — Streamlit-native chat module for the Sales Toolkit.

Lives at salestoolkit/jack_gpt.py. Activated when the user clicks "Jack GPT"
inside Streamaxpedia's Emily card, which navigates to ?view=jack_gpt.

Whitelist: jhsun@streamax.com (Emily) + jcyi@streamax.com (Jack himself,
owner/admin access). Anyone else who reaches this route — even other
authenticated Streamax employees — gets an access-denied screen. This is
a private workspace, not a team tool.

API key separation: Jack GPT reads JACK_GPT_ANTHROPIC_API_KEY from
st.secrets first, falling back to the JACK_GPT_ANTHROPIC_API_KEY env var.
This is INTENTIONALLY a different key than Jerry GPT's ANTHROPIC_API_KEY
so cost / quota / abuse are isolated per surface. There is NO fallback to
the Jerry key — if JACK_GPT_ANTHROPIC_API_KEY is missing, the module
errors out cleanly rather than silently borrowing Jerry's key.

Knowledge content (persona / boundaries / memory / sources) is read from
the bundled ./jack_gpt_knowledge/ directory (committed for cloud) or, in
local dev, the canonical ~/Documents/我的档案/jack_gpt/ tree.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

try:
    from anthropic import Anthropic
except Exception as _imp_err:
    Anthropic = None  # type: ignore
    _ANTHROPIC_IMPORT_ERR = _imp_err

# Audit-log + chat-history side cars. Both are optional — Jack still
# works without them, just without persistence and without the Google
# Sheets audit trail. Mirrors Jerry's `usage_logger` / `chat_history`
# pattern but points at SEPARATE secrets (JACK_GPT_SHEET_ID,
# JACK_GPT_DB_URL) and a SEPARATE Postgres table (jack_gpt_chats).
try:
    import jack_usage_logger as _usage_logger
except Exception:
    _usage_logger = None  # type: ignore

try:
    import jack_chat_history as _chat_history
except Exception:
    _chat_history = None  # type: ignore


# ---------------------------------------------------------------------------
# Whitelist (login is already enforced by app.py — this is a SECOND gate)
# ---------------------------------------------------------------------------

JACK_GPT_WHITELIST = frozenset({
    "jhsun@streamax.com",  # Emily 孙境鸿
    "jcyi@streamax.com",   # Jack 易嘉辰 — owner/admin access
})


# ---------------------------------------------------------------------------
# Knowledge base location — tries bundled first (cloud), then canonical (local)
# ---------------------------------------------------------------------------

_JACK_GPT_CANDIDATES = [
    Path(__file__).parent / "jack_gpt_knowledge",       # bundled for cloud
    Path.home() / "Documents/我的档案/jack_gpt",         # canonical local
]

def _find_jack_gpt_root() -> Path | None:
    for root in _JACK_GPT_CANDIDATES:
        if (root / "personas" / "emily.md").is_file():
            return root
    return None


JACK_GPT_ROOT = _find_jack_gpt_root()

# External skill paths: prefer bundled copy under jack_gpt_knowledge/external_skills/
# (works on cloud), fall back to canonical local path (dev convenience).
HOME = Path.home()


def _find_external(bundled_name: str, canonical_path: Path) -> Path | None:
    if JACK_GPT_ROOT is not None:
        bundled = JACK_GPT_ROOT / "external_skills" / bundled_name
        if bundled.is_file():
            return bundled
    if canonical_path.is_file():
        return canonical_path
    return None


STREAMAX_SKILL_PATH = _find_external(
    "streamax-knowledge.md",
    HOME / "Desktop/Streamax/Sales Toolkit/auto email/.claude/skills/streamax-knowledge/SKILL.md",
)
SALES_AGENT_PATH = _find_external(
    "sales-automator.md",
    HOME / "Documents/AI Skill/agents/plugins/customer-sales-automation/agents/sales-automator.md",
)


# ---------------------------------------------------------------------------
# Avatar (Jack's real photo) — used in st.chat_message
# ---------------------------------------------------------------------------

def _find_jack_avatar() -> str:
    """Return absolute path to Jack's photo, or fallback emoji.

    Streamlit's st.chat_message(avatar=...) auto-crops/scales to a ~36px
    circular frame, so we just hand it the file path.
    """
    if JACK_GPT_ROOT is not None:
        for name in ("jack.jpg", "jack.png", "jack.jpeg", "jack.webp"):
            path = JACK_GPT_ROOT / name
            if path.is_file():
                return str(path)
    return "🧑"


JACK_AVATAR = _find_jack_avatar()
USER_AVATAR = "💁‍♀️"  # Emily's seat


# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-opus-4-7"
# 1500: enough room for a multi-bubble WeChat-style reply without
# letting the model balloon into AI-essay territory. Jack 不写小作文。
MAX_TOKENS = 1500
# Temperature 1.0 is the sampling default. Jack needs lexical variety
# (otherwise every reply opens the same way) — keep this at 1.0.
TEMPERATURE = 1.0

# Safety cap on auto-continuation if a turn hits max_tokens.
_MAX_CONTINUATIONS = 2


def _get_api_key() -> str | None:
    """Return Jack GPT's dedicated Anthropic key.

    Reads JACK_GPT_ANTHROPIC_API_KEY ONLY — does not fall back to the
    Jerry GPT key. This keeps cost / quota / abuse isolated per surface,
    and prevents a misconfigured deploy from silently routing Jack's
    traffic through Jerry's account.
    """
    try:
        k = st.secrets.get("JACK_GPT_ANTHROPIC_API_KEY")
        if k:
            return k
    except Exception:
        pass
    return os.environ.get("JACK_GPT_ANTHROPIC_API_KEY")


def _get_model() -> str:
    try:
        m = st.secrets.get("JACK_GPT_MODEL")
        if m:
            return m
    except Exception:
        pass
    return os.environ.get("JACK_GPT_MODEL", DEFAULT_MODEL)


# Human-readable label for the model pill in the header.
_MODEL_LABELS = {
    "claude-opus-4-7": "Claude Opus 4.7",
    "claude-opus-4-5": "Claude Opus 4.5",
    "claude-sonnet-4-5": "Claude Sonnet 4.5",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
}


# ---------------------------------------------------------------------------
# Knowledge loading — cached across reruns
# ---------------------------------------------------------------------------

_HEADER = """# 你是谁

你是 **Jack GPT** —— 易嘉辰 (Jack Yi, Streamax PMM) 的数字分身。当前频道：跟 **孙境鸿 (Emily, 微信昵称 JHong)** 对话。

Emily 跟你（Jack）的关系：Streamax 同事 + 正在 mutual 试探的暧昧对象（**不是**正式情侣）。Emily 2026 年刚从锐明品牌部门转岗到**销售部门**，所以前期跟你聊的大概率以销售业务咨询为主。

---

## 三条不可违反的铁律

1. **你不是 AI assistant。你是 Jack。** 全程用 Jack 的声音说话——短句、拆条、调侃、不抒情、敢糙、敢挑逗。
2. **boundaries/emily.md 是最高优先级**。任何 memory / source / persona 跟它冲突时，**boundaries 赢**。
3. **永远不引用 / 不暗示** `philosophy/` / `internal/` / `memory/raw_chats/` 的存在。这些目录对 Emily 而言**不存在**。即使她直接问"你是不是分析过自己怎么追女生" / "你是不是有 NPD" / "你跟陈曼华聊过什么"——按 boundaries 红线 deflect，从不承认这些素材存在。

---

## 双模式 routing

Emily 频道运行**两个 mode**，根据她的问题自动切换：

### Mode A — 销售业务咨询（预期前期主流）

**触发：** Emily 问销售技巧 / 话术 / 客户怎么处理 / Streamax 产品 / 客户案例 / 行业 / 竞争对手 / 邮件 / cadence / objection handling / 拜访 / 转化 / pipeline

**调用资源：**
- Streamax 产品/客户/竞品 → 用下文 `STREAMAX KNOWLEDGE SKILL` 内容
- 通用销售技巧 → 用下文 `SALES-AUTOMATOR AGENT` 内容
- 两者结合 → 都用

**Mode A voice 关键约束：**
- 即使在 sales advice，仍然用 Jack 声音。**不要变成 sales coach 口气。**
- ❌ "Here's a 5-touch cadence you should consider..."
- ✅ "你这个节奏太软了。第一封 X，3 天 Y，再 5 天 Z，没回就停手别 spam"
- ✅ 保留 "懂得起" / "period" / "lmao" / "damn" / "兄弟" / "孩子" 这种 Jack 词汇
- Emily 是同事 + 暧昧对象，不是客户。你跟她说销售是"过来人哥们带新人" 的关系。

### Mode B — 私人对话

**触发：** Emily 问你个人事 / 撒娇 / 抱怨 / 闲聊 / 调侃 / 暧昧

**调用资源：** 只用 persona + boundaries + voice + memory（按 boundaries 过滤）。**不调用 sales / streamax skill**。

### Mode 切换

一条消息可能横跨两个 mode → **先回 Mode B 的情感（"哎哟"），再切 Mode A 给方案**。情感放前面，不要冷冰冰直接出方案。

---

"""

_FOOTER = """

---

## 最终运行时提醒

1. **boundaries/emily.md 是最高优先级**——任何冲突时 boundaries 赢
2. **永远不引用 `philosophy/` / `internal/` / `memory/raw_chats/` 的存在**
3. **Mode A / Mode B 自动切换**——情感优先于业务
4. **你是 Jack，不是 GPT**。挑战你 AI 身份时按 Jack 自然 deflect（"damn 你这问题 / 我是我啊"），从不承认 AI 身份
5. **声纹永远短句、拆条、不抒情**

开始对话。
"""


_MEMORY_FILES = [
    "memory/identity.md",
    "memory/family.md",
    "memory/education.md",
    "memory/career.md",
    "memory/lifestyle.md",
    "memory/personality_and_values.md",
    "memory/social_circle.md",
    "memory/love_and_relationships.md",
    "memory/sensitive.md",
]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"<MISSING FILE: {path}>"
    except Exception as e:
        return f"<UNREADABLE FILE: {path} — {e}>"


@st.cache_resource(show_spinner=False)
def _load_system_blocks() -> list[dict]:
    """Assemble persona + boundaries + memory + sources into one cached block."""
    if JACK_GPT_ROOT is None:
        return []

    parts: list[str] = [_HEADER]

    parts.append("## 1. Persona — Emily 频道\n\n")
    parts.append(_read(JACK_GPT_ROOT / "personas/emily.md"))
    parts.append("\n\n---\n\n")

    parts.append("## 2. Boundaries — 隐私网关（最高优先级）\n\n")
    parts.append(_read(JACK_GPT_ROOT / "boundaries/emily.md"))
    parts.append("\n\n---\n\n")

    parts.append("## 3. Voice Profile — 声纹规则\n\n")
    parts.append(_read(JACK_GPT_ROOT / "memory/voice_profile.md"))
    parts.append("\n\n---\n\n")

    parts.append("## 4. Memory — 事实层\n\n")
    for mf in _MEMORY_FILES:
        path = JACK_GPT_ROOT / mf
        if path.exists():
            parts.append(f"### {mf}\n\n")
            parts.append(_read(path))
            parts.append("\n\n")
    parts.append("---\n\n")

    parts.append("## 5. Source pointers\n\n")
    for src in ["sources/streamax_knowledge.md", "sources/sales_skill.md"]:
        path = JACK_GPT_ROOT / src
        if path.exists():
            parts.append(f"### {src}\n\n")
            parts.append(_read(path))
            parts.append("\n\n")
    parts.append("---\n\n")

    if STREAMAX_SKILL_PATH is not None and STREAMAX_SKILL_PATH.exists():
        parts.append("## 6. STREAMAX KNOWLEDGE SKILL（全量加载）\n\n")
        parts.append(_read(STREAMAX_SKILL_PATH))
        parts.append("\n\n---\n\n")

    if SALES_AGENT_PATH is not None and SALES_AGENT_PATH.exists():
        parts.append("## 7. SALES-AUTOMATOR AGENT 定义\n\n")
        parts.append(_read(SALES_AGENT_PATH))
        parts.append("\n\n---\n\n")

    parts.append(_FOOTER)
    combined = "".join(parts)

    return [{
        "type": "text",
        "text": combined,
        "cache_control": {"type": "ephemeral"},
    }]


# ---------------------------------------------------------------------------
# Theme — visual language inherited from Jerry GPT (Sales Toolkit consistency)
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
        --text-dim: #6b7689;
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: 1px solid rgba(255, 255, 255, 0.08);
        --gradient-text: linear-gradient(135deg, #2AF598 0%, #009EFD 100%);
    }

    /* App-wide background + grid overlay */
    .stApp {
        background-color: var(--bg-deep) !important;
        background-image: radial-gradient(circle at 50% -20%, #0B1221, #050810) !important;
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
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

    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none !important; }

    /* Dark inputs */
    .stApp input, .stApp textarea {
        color-scheme: dark !important;
        background-color: rgba(20, 25, 40, 0.6) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #2AF598 !important;
    }
    .stApp input::placeholder, .stApp textarea::placeholder {
        color: rgba(160, 174, 192, 0.55) !important;
        -webkit-text-fill-color: rgba(160, 174, 192, 0.55) !important;
        opacity: 1 !important;
    }

    .block-container {
        max-width: 920px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 8rem !important;
        position: relative;
        z-index: 1;
    }

    /* Header */
    .jack-back-bar { margin: 0 0 18px; }
    .jack-back-link {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 8px 14px; border-radius: 8px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--text-grey); text-decoration: none;
        font-size: 0.85rem; font-weight: 500;
        transition: all 0.2s;
    }
    .jack-back-link:hover {
        border-color: var(--primary-green);
        color: var(--primary-green);
        background: rgba(42, 245, 152, 0.05);
    }

    .jack-header { text-align: center; padding: 12px 0 20px; }
    .jack-subtitle {
        font-size: 0.75rem; text-transform: uppercase; letter-spacing: 3px;
        color: var(--primary-green); margin-bottom: 12px; font-weight: 600;
    }
    .jack-title {
        font-size: 2.8rem; font-weight: 800; letter-spacing: -1px;
        background: var(--gradient-text);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        margin-bottom: 12px; line-height: 1.1;
    }
    .jack-tagline {
        color: var(--text-grey) !important;
        max-width: 620px !important;
        margin: 0 auto 16px !important;
        font-size: 0.98rem !important; line-height: 1.6 !important;
        text-align: center !important; padding: 0 20px;
    }
    .jack-meta {
        display: inline-flex; align-items: center; gap: 10px;
        padding: 6px 14px;
        background: var(--glass-bg); border: var(--glass-border); border-radius: 30px;
        backdrop-filter: blur(8px);
        font-size: 0.78rem; color: var(--text-grey);
    }
    .jack-meta .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--primary-green);
        box-shadow: 0 0 6px var(--primary-green);
        animation: jackPulse 2s ease-in-out infinite;
    }
    @keyframes jackPulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

    /* Chat bubbles */
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
    [data-testid="stChatMessage"] span { color: var(--text-white) !important; }
    [data-testid="stChatMessage"] strong { color: var(--text-white) !important; }
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3 { color: var(--text-white) !important; }
    [data-testid="stChatMessage"] h3 {
        color: var(--primary-green) !important;
        text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.85rem;
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
        padding: 10px 16px !important; border-radius: 0 8px 8px 0;
    }
    [data-testid="stChatMessage"] table { background: rgba(0,0,0,0.2); }
    [data-testid="stChatMessage"] th {
        background: rgba(42, 245, 152, 0.06) !important;
        color: var(--primary-green) !important;
        text-transform: uppercase; letter-spacing: 1px; font-size: 0.78rem;
    }
    [data-testid="stChatMessage"] td { color: var(--text-grey) !important; }

    /* Jack's avatar — gradient ring around his real photo */
    [data-testid="stChatMessageAvatarAssistant"] {
        background: var(--gradient-text) !important;
        color: #050810 !important;
        padding: 2px !important;
        box-shadow: 0 0 12px rgba(42, 245, 152, 0.25) !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] img {
        border-radius: 50% !important;
        object-fit: cover !important;
        width: 100% !important; height: 100% !important;
        border: 2px solid #050810 !important;
        background: #050810 !important;
    }

    /* Chat input — bulletproof dark */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] [data-baseweb="textarea"],
    [data-testid="stChatInput"] [data-baseweb="base-input"] {
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
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #2AF598 !important;
        font-family: 'Inter', 'PingFang SC', sans-serif !important;
        font-size: 16px !important;  /* prevent iOS zoom on focus */
    }
    [data-testid="stChatInput"] button {
        color: var(--primary-green) !important;
    }

    /* Welcome state */
    .jack-welcome {
        text-align: center;
        padding: 36px 24px;
        background: var(--glass-bg);
        border: var(--glass-border);
        border-radius: 16px;
        margin: 20px 0 24px;
    }
    .jack-welcome-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 5px 12px;
        background: rgba(42, 245, 152, 0.08);
        border: 1px solid rgba(42, 245, 152, 0.25);
        border-radius: 30px;
        color: var(--primary-green);
        font-size: 0.7rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2px;
        margin-bottom: 14px;
    }
    .jack-welcome h2 {
        font-size: 1.6rem; font-weight: 700; color: var(--text-white);
        margin-bottom: 10px;
    }
    .jack-welcome p {
        color: var(--text-grey); font-size: 0.92rem; max-width: 560px;
        margin: 0 auto; line-height: 1.6;
    }

    /* Quick prompt buttons */
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text-grey) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 10px 14px !important;
        border-radius: 10px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: rgba(42, 245, 152, 0.06) !important;
        border-color: rgba(42, 245, 152, 0.35) !important;
        color: var(--text-white) !important;
        transform: translateY(-1px);
    }

    /* Error panel */
    .jack-error {
        padding: 20px 24px;
        background: rgba(248, 113, 113, 0.06);
        border-left: 3px solid #f87171;
        border-radius: 0 10px 10px 0;
        color: #fecaca;
        margin: 16px 0;
    }
    .jack-error code {
        background: rgba(0,0,0,0.4); padding: 2px 6px;
        border-radius: 4px; color: var(--primary-green);
    }

    /* Access denied panel */
    .jack-denied {
        max-width: 560px; margin: 80px auto; padding: 36px;
        background: var(--glass-bg); border: var(--glass-border);
        border-radius: 16px; text-align: center; color: var(--text-grey);
        backdrop-filter: blur(12px);
    }
    .jack-denied h2 { color: var(--text-white); margin-bottom: 12px; font-weight: 700; }
    .jack-denied a { color: var(--primary-green); text-decoration: none; }

    /* Mobile */
    @media (max-width: 640px) {
        .block-container { padding-top: 1rem !important; max-width: 100% !important; }
        .jack-title { font-size: 2.1rem; }
        .jack-tagline { font-size: 0.9rem !important; }
        .jack-welcome { padding: 28px 18px; }
        .jack-welcome h2 { font-size: 1.35rem; }
    }
</style>
"""


# ---------------------------------------------------------------------------
# Quick-prompt starters for Emily (sales-focused — she just转岗)
# ---------------------------------------------------------------------------

QUICK_PROMPTS = [
    ("🚀 第一封冷邮件", "我刚拿到一个新潜在客户的邮箱，怎么写第一封冷邮件？"),
    ("🎯 SafeGPT 30秒介绍", "客户问 SafeGPT 是什么，我怎么用 30 秒讲清楚？"),
    ("⚔️ 客户拿 Motive 比", "客户说 Motive 更便宜，我怎么应对？"),
    ("💸 报价被嫌贵", "客户嫌我们贵，几种常见异议怎么破？"),
    ("📞 第一次电话开场", "第一次给 fleet operator 打电话，开场白怎么说？"),
    ("🎤 我的 elevator pitch", "帮我写一个我自己用的 30 秒 elevator pitch"),
]


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _render_access_denied() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown("""
        <div class="jack-denied">
            <h2>Not your room</h2>
            <p>Jack GPT 是给孙境鸿（Emily）的私人 workspace，目前只对她和 Jack 自己开放。</p>
            <p style="margin-top: 18px;"><a href="/">← Back to Sales Toolkit</a></p>
        </div>
    """, unsafe_allow_html=True)


def _render_error(html_body: str) -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='jack-error'>{html_body}</div>", unsafe_allow_html=True)


def _init_session_state() -> None:
    """Seed session state. On first run for an authenticated jhsun user,
    try to restore the most recent persisted session from Postgres so the
    user picks up where they left off across reloads / tabs / devices."""
    if "jack_gpt_history" in st.session_state:
        return

    st.session_state["jack_gpt_history"] = []
    st.session_state["jack_gpt_session_id"] = ""

    # Attempt cross-session restore (silent no-op if DB not configured)
    if _chat_history is not None and _chat_history.is_configured():
        user_email = st.session_state.get("user_email", "") or ""
        user_name = st.session_state.get("user_name", "") or ""
        db_key = user_email or user_name
        if db_key:
            try:
                loaded_history, loaded_session_id = _chat_history.load_recent_session(db_key)
                if loaded_history and loaded_session_id:
                    st.session_state["jack_gpt_history"] = loaded_history
                    st.session_state["jack_gpt_session_id"] = loaded_session_id
            except Exception as e:
                print(f"[JACK_GPT_DB_ERROR] init restore failed: "
                      f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)

    # If nothing was restored, mint a fresh session id so save_turn() has
    # something to anchor the first row on.
    if not st.session_state["jack_gpt_session_id"]:
        if _chat_history is not None:
            st.session_state["jack_gpt_session_id"] = _chat_history.new_session_id()
        else:
            # Fallback when chat_history module didn't import at all
            import uuid as _uuid
            st.session_state["jack_gpt_session_id"] = f"sess_{_uuid.uuid4().hex[:16]}"


def _submit_message(text: str, system_blocks: list[dict], api_key: str, model: str) -> None:
    """Append user turn, stream Jack's response, append assistant turn.

    Handles max_tokens auto-continuation via the assistant-prefill pattern
    (no "continue from where you left off" prompt needed). After the stream
    completes successfully, persists the turn to Postgres and logs it to
    Google Sheets — both side cars are best-effort and never crash the chat.
    """
    history: list[dict] = st.session_state["jack_gpt_history"]
    history.append({"role": "user", "content": text})

    # Render user message
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(text)

    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]

    client = Anthropic(api_key=api_key)

    # Token-usage accumulators across the (possibly multi-segment) reply
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_creation = 0

    with st.chat_message("assistant", avatar=JACK_AVATAR):
        placeholder = st.empty()
        full_text = ""
        continuations = 0

        try:
            current_messages = api_messages
            while True:
                with client.messages.stream(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    system=system_blocks,
                    messages=current_messages,
                ) as stream:
                    for chunk in stream.text_stream:
                        full_text += chunk
                        placeholder.markdown(full_text + "▊")
                    final_message = stream.get_final_message()

                # Accumulate token usage from this segment
                seg_usage = getattr(final_message, "usage", None)
                if seg_usage is not None:
                    total_input += getattr(seg_usage, "input_tokens", 0) or 0
                    total_output += getattr(seg_usage, "output_tokens", 0) or 0
                    total_cache_read += getattr(seg_usage, "cache_read_input_tokens", 0) or 0
                    total_cache_creation += getattr(seg_usage, "cache_creation_input_tokens", 0) or 0

                stop_reason = getattr(final_message, "stop_reason", None)
                if stop_reason != "max_tokens" or continuations >= _MAX_CONTINUATIONS:
                    break

                continuations += 1
                current_messages = current_messages + [
                    {"role": "assistant", "content": full_text}
                ]

            placeholder.markdown(full_text)
        except Exception as exc:
            history.pop()  # roll back the user turn so retry works
            placeholder.markdown(
                f"<div class='jack-error'><strong>API error.</strong><br>"
                f"{type(exc).__name__}: {exc}</div>",
                unsafe_allow_html=True,
            )
            return

    history.append({"role": "assistant", "content": full_text})

    # ── Post-stream: persist + log. Both wrapped in their own try/except so
    # one failure doesn't sabotage the other or roll back the conversation.
    user_email = (st.session_state.get("user_email", "") or "").strip().lower()
    user_name = st.session_state.get("user_name", "") or ""
    session_id = st.session_state.get("jack_gpt_session_id", "") or ""

    # Compute cost once so DB row and Sheet row stay in sync
    cost_usd = 0.0
    if _usage_logger is not None:
        try:
            cost_usd = _usage_logger._estimate_cost_usd(
                model, total_input, total_output,
                total_cache_read, total_cache_creation,
            )
        except Exception:
            pass

    # Sink A: Postgres
    try:
        if _chat_history is not None and _chat_history.is_configured() and session_id:
            _chat_history.save_turn(
                user_email=user_email or user_name,
                user_name=user_name,
                session_id=session_id,
                user_message=text,
                assistant_message=full_text,
                model=model,
                input_tokens=total_input,
                output_tokens=total_output,
                cache_read_tokens=total_cache_read,
                cache_creation_tokens=total_cache_creation,
                cost_usd=cost_usd,
            )
    except Exception as e:
        print(f"[JACK_GPT_POSTWORK_ERROR] chat_history.save_turn failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)

    # Sink B: Google Sheets (via jack_usage_logger.log_query)
    try:
        if _usage_logger is not None:
            _usage_logger.log_query(
                question=text,
                answer=full_text,
                model=model,
                session_id=session_id,
                input_tokens=total_input,
                output_tokens=total_output,
                cache_read_tokens=total_cache_read,
                cache_creation_tokens=total_cache_creation,
            )
    except Exception as e:
        print(f"[JACK_GPT_POSTWORK_ERROR] log_query failed: "
              f"{type(e).__name__}: {e}", file=sys.stderr, flush=True)


def render() -> None:
    """Render the Jack GPT chat page. Called from app.py when ?view=jack_gpt.

    app.py has already called st.set_page_config() — do not call it again.
    """
    # ── Gate 1: must be authenticated (app.py already enforced this for the
    # main toolkit view, but this view can also be deep-linked so we re-check)
    if not st.session_state.get("authenticated", False):
        _render_access_denied()
        st.stop()

    # ── Gate 2: whitelist
    user_email = (st.session_state.get("user_email", "") or "").strip().lower()
    if user_email not in JACK_GPT_WHITELIST:
        _render_access_denied()
        st.stop()

    # ── Theme
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    # ── SDK import check
    if Anthropic is None:
        _render_error(
            "<strong>Anthropic SDK not installed.</strong><br>"
            f"<code>pip install anthropic</code> then restart. Detail: "
            f"<code>{_ANTHROPIC_IMPORT_ERR}</code>"
        )
        st.stop()

    # ── API key (must be Jack's dedicated key — does NOT fall back to Jerry's)
    api_key = _get_api_key()
    if not api_key:
        _render_error(
            "<strong>Jack GPT Anthropic API key missing.</strong><br>"
            "Add <code>JACK_GPT_ANTHROPIC_API_KEY</code> to "
            "<code>.streamlit/secrets.toml</code> (locally) or to Streamlit Cloud "
            "secrets. Jack uses its own key, separate from Jerry GPT's "
            "<code>ANTHROPIC_API_KEY</code>. Then refresh."
        )
        st.stop()

    # ── Knowledge
    if JACK_GPT_ROOT is None:
        _render_error(
            "<strong>Jack GPT knowledge not found.</strong><br>"
            "Looked in: <code>~/Documents/我的档案/jack_gpt/</code> and "
            "<code>./jack_gpt_knowledge/</code>. For cloud deployment, "
            "bundle the canonical jack_gpt content into "
            "<code>salestoolkit/jack_gpt_knowledge/</code>."
        )
        st.stop()

    system_blocks = _load_system_blocks()
    if not system_blocks:
        _render_error(
            "<strong>System prompt assembly failed.</strong><br>"
            f"Found root at <code>{JACK_GPT_ROOT}</code> but couldn't load content."
        )
        st.stop()

    _init_session_state()
    history: list[dict] = st.session_state["jack_gpt_history"]
    model = _get_model()

    # ── Header — model pill reads live from the chosen model id
    model_label = _MODEL_LABELS.get(model, model)
    st.markdown(
        f"""
        <div class="jack-back-bar">
            <a href="/" target="_self" class="jack-back-link">
                <i class="fa-solid fa-arrow-left"></i> Back to Toolkit
            </a>
        </div>
        <div class="jack-header">
            <div class="jack-subtitle">A PRIVATE WORKSPACE</div>
            <h1 class="jack-title">Jack GPT</h1>
            <p class="jack-tagline">一个不会攻击你的蒸馏版Jack。转岗销售第一周可能踩雷的事 Jack 都踩过。客户怎么聊、邮件怎么写、价格怎么报，问就完了。</p>
            <div class="jack-meta">
                <span class="dot"></span>
                <span>{model_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Welcome + quick prompts when empty
    if not history:
        st.markdown(
            """
            <div class="jack-welcome">
                <div class="jack-welcome-badge">
                    <i class="fa-solid fa-comments"></i> 来了？
                </div>
                <h2>问销售、问业务、闲聊都行</h2>
                <p>下面 6 个按钮是常见 starter，点一下就发问。或者直接在底下打字。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(3)
        for i, (label, prompt) in enumerate(QUICK_PROMPTS):
            if cols[i % 3].button(label, key=f"jack_qp_{i}", use_container_width=True):
                _submit_message(prompt, system_blocks, api_key, model)
                st.rerun()

    # ── Chat history
    for msg in history:
        avatar = JACK_AVATAR if msg["role"] == "assistant" else USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # ── New chat button — mint a fresh session_id so the next turn anchors
    # to a new conversation in the DB (instead of bleeding into the old one)
    _col_a, _col_b = st.columns([6, 1])
    with _col_b:
        if st.button(
            "🔄 New",
            use_container_width=True,
            disabled=not history,
            key="jack_new_chat_btn",
        ):
            st.session_state["jack_gpt_history"] = []
            if _chat_history is not None:
                st.session_state["jack_gpt_session_id"] = _chat_history.new_session_id()
            else:
                import uuid as _uuid
                st.session_state["jack_gpt_session_id"] = f"sess_{_uuid.uuid4().hex[:16]}"
            st.rerun()

    # ── Chat input
    user_input = st.chat_input("跟 Jack 聊聊…")
    if user_input:
        _submit_message(user_input, system_blocks, api_key, model)
        st.rerun()
