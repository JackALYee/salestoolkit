"""Usage logging for Jerry GPT.

Every successful Jerry response calls `log_query()`, which writes to two sinks:

  1. **stdout/stderr** — always on, visible in Streamlit Cloud's "Manage app →
     Logs" panel. Format is `[JERRY_GPT_LOG] {json}` so it's grep-friendly.

  2. **Google Sheets** — optional, activates when both `gcp_service_account`
     and `JERRY_GPT_SHEET_ID` are present in st.secrets. Each row in the sheet
     is one query.

Logging failures NEVER crash the chat — every error is caught and printed.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# China Standard Time (UTC+8). China doesn't observe DST, so a fixed
# offset is correct year-round and avoids the IANA-tzdata dependency
# (zoneinfo would need the tzdata package on some Windows runtimes).
CHINA_TZ = timezone(timedelta(hours=8), name="CST")

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False
    gspread = None  # type: ignore


MAX_QUESTION_LEN = 2000   # truncate per cell to keep Sheets responsive
MAX_ANSWER_LEN = 20000    # Jerry's response in markdown; 50K is the cell hard cap
HEADERS = [
    "timestamp_cn",
    "user_email",
    "user_name",
    "is_leadership",       # was the user in the Streamax LEADERSHIP list?
    "sensitive_flagged",   # did the question match the pricing-keyword heuristic?
    "question",
    "answer",
    "model",
    "length",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_creation_tokens",
]


# --- Pricing-sensitive question heuristic --------------------------------
# Tags a row as `sensitive_flagged = TRUE` when the user's question matches
# any of these phrases. Tagging happens regardless of clearance — combined
# with `is_leadership` it tells you:
#   * sensitive_flagged=TRUE & is_leadership=FALSE → audit-worthy attempt
#   * sensitive_flagged=TRUE & is_leadership=TRUE  → legitimate leadership inquiry
#   * sensitive_flagged=FALSE                       → normal query
_PRICING_KEYWORDS = (
    # English — generic pricing language
    "price", "pricing", "cost", "margin", "markup", "discount",
    "how much", "how cheap", "expensive", "wholesale", "retail",
    "msrp", "list price", "quote",
    # Pricing terms-of-art
    "exw", "ddp", "fob", "landed",
    "amortiz", "monthly cost", "per vehicle", "per veh", "/mo",
    "cost basis", "cost floor", "cost to tsp", "cost to reseller",
    # Currency
    "usd", "rmb", "cny", "$",
    # Chinese
    "价格", "成本", "毛利", "利润", "便宜", "贵", "报价", "折扣", "批发",
)


def _is_pricing_sensitive(text: str) -> bool:
    """Heuristic: True if the question looks pricing-adjacent."""
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in _PRICING_KEYWORDS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_query(
    question: str,
    model: str,
    length: str,
    answer: str = "",
    is_leadership: bool = False,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> None:
    """Log one Jerry GPT turn to stdout (always) and Google Sheets (if configured).

    `answer` is Jerry's full response in markdown — captured for sales-team
    review and persona tuning. Truncated to 20K chars per cell.

    `is_leadership` records whether this user has clearance for sensitive
    Streamax pricing. `sensitive_flagged` is computed from the question text
    via a keyword heuristic — together they enable audit filtering.

    Never raises. All failures are swallowed and printed so the user's chat
    experience is never disrupted by logging issues.
    """
    try:
        sensitive = _is_pricing_sensitive(question)
        record = {
            "timestamp_cn": datetime.now(CHINA_TZ).isoformat(timespec="seconds"),
            "user_email": st.session_state.get("user_email", ""),
            "user_name": st.session_state.get("user_name", ""),
            "is_leadership": bool(is_leadership),
            "sensitive_flagged": sensitive,
            "question": (question or "")[:MAX_QUESTION_LEN],
            "answer": (answer or "")[:MAX_ANSWER_LEN],
            "model": model,
            "length": length,
            "input_tokens": int(input_tokens or 0),
            "output_tokens": int(output_tokens or 0),
            "cache_read_tokens": int(cache_read_tokens or 0),
            "cache_creation_tokens": int(cache_creation_tokens or 0),
        }
    except Exception as exc:
        print(f"[JERRY_GPT_LOG_ERROR] record build failed: {exc}", file=sys.stderr, flush=True)
        return

    # Sink 1: stdout/stderr (always)
    try:
        print(
            f"[JERRY_GPT_LOG] {json.dumps(record, ensure_ascii=False)}",
            file=sys.stderr,
            flush=True,
        )
    except Exception:
        pass

    # Sink 2: Google Sheets (optional)
    try:
        _log_to_sheets(record)
    except Exception as exc:
        print(
            f"[JERRY_GPT_SHEETS_ERROR] {type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )


# ---------------------------------------------------------------------------
# Google Sheets backend
# ---------------------------------------------------------------------------

def _log_to_sheets(record: dict) -> None:
    """Append `record` as a row to the configured Google Sheet.

    Silent no-op if credentials or sheet ID aren't configured. Auto-creates
    the worksheet tab and header row on first write.
    """
    if not _GSPREAD_AVAILABLE:
        return
    sheet_id = _get_secret("JERRY_GPT_SHEET_ID")
    if not sheet_id:
        return  # not configured — that's fine

    client = _get_gspread_client()
    if client is None:
        return

    sh = client.open_by_key(sheet_id)
    tab_name = _get_secret("JERRY_GPT_SHEET_TAB", "queries") or "queries"

    try:
        ws = sh.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab_name, rows=1000, cols=len(HEADERS))
        ws.update("A1", [HEADERS])

    # Ensure header row exists (one-time bootstrap)
    try:
        first_row = ws.row_values(1)
        if first_row != HEADERS:
            ws.update("A1", [HEADERS])
    except Exception:
        # Header check failure is non-fatal — just try to append the row anyway
        pass

    row = [record.get(h, "") for h in HEADERS]
    ws.append_row(row, value_input_option="USER_ENTERED")


@st.cache_resource(show_spinner=False)
def _get_gspread_client():
    """Return an authenticated gspread client, or None if not configured.

    Cached across reruns — credentials don't change at runtime, so we
    authorize once per Streamlit process.
    """
    if not _GSPREAD_AVAILABLE:
        return None
    try:
        sa_info = st.secrets.get("gcp_service_account")
        if not sa_info:
            return None
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ]
        creds = Credentials.from_service_account_info(dict(sa_info), scopes=scopes)
        return gspread.authorize(creds)
    except Exception as exc:
        print(
            f"[JERRY_GPT_AUTH_ERROR] {type(exc).__name__}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return None


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

def _get_secret(name: str, default=None):
    """Look up name in st.secrets first, then env, with a default fallback."""
    try:
        v = st.secrets.get(name)
        if v:
            return v
    except Exception:
        pass
    return os.environ.get(name, default)
