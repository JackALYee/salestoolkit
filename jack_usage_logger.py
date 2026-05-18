"""Usage logging for Jack GPT — Emily-only private workspace.

Mirrors `usage_logger.py` (Jerry's logger) but targets a SEPARATE Google
Sheet via SEPARATE secrets so the two surfaces never share an audit
trail:

  - `JACK_GPT_SHEET_ID`            — Sheet ID for Jack's audit log
  - `JACK_GPT_SHEET_TAB`           — optional tab name (defaults to "queries")
  - `[jack_gpt_service_account]`   — optional GCP service-account TOML table
                                     dedicated to Jack. If absent, falls back
                                     to the shared `[gcp_service_account]`
                                     table — the same credential can write to
                                     both Jerry's and Jack's sheets as long
                                     as the service account email is added
                                     as Editor on both spreadsheets.

Every successful Jack response calls `log_query()`, which writes to two sinks:

  1. **stdout/stderr** — always on, visible in Streamlit Cloud's "Manage app
     → Logs" panel. Format is `[JACK_GPT_LOG] {json}`.

  2. **Google Sheets** — optional, activates when `JACK_GPT_SHEET_ID` plus a
     service-account credential are available.

Schema is simpler than Jerry's because Jack has no model selector, no length
selector, and no LEADERSHIP / sensitivity gating (whitelist is jhsun-only,
so every row is from the same authorized user).

Logging failures NEVER crash the chat — every error is caught and printed.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# China Standard Time (UTC+8). Matches Jerry's audit-log convention so logs
# from both surfaces are directly comparable when filtered by timestamp.
CHINA_TZ = timezone(timedelta(hours=8), name="CST")

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False
    gspread = None  # type: ignore


MAX_QUESTION_LEN = 2000
MAX_ANSWER_LEN = 20000

HEADERS = [
    "timestamp_cn",
    "user_email",
    "user_name",
    "session_id",
    "question",
    "answer",
    "model",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_creation_tokens",
    "cost_usd",
]


# --- Per-million-token pricing for cost estimation (USD) ---------------------
# Identical table to usage_logger.PRICING so Jerry and Jack rows in their
# respective sheets stay directly comparable. When updating one, update both.
PRICING = {
    "claude-opus-4-7":           {"input": 15.00, "output": 75.00, "cache_read": 1.50,  "cache_creation": 18.75},
    "claude-sonnet-4-6":         {"input":  3.00, "output": 15.00, "cache_read": 0.30,  "cache_creation":  3.75},
    "claude-haiku-4-5-20251001": {"input":  0.80, "output":  4.00, "cache_read": 0.08,  "cache_creation":  1.00},
}
_PRICING_FALLBACK = PRICING["claude-opus-4-7"]  # Jack defaults to opus 4.7


def _estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int,
    cache_creation_tokens: int,
) -> float:
    """Estimate per-request cost in USD. Rounded to 6 decimals for sub-cent precision."""
    rates = PRICING.get(model, _PRICING_FALLBACK)
    total = (
        (input_tokens or 0) * rates["input"]
        + (output_tokens or 0) * rates["output"]
        + (cache_read_tokens or 0) * rates["cache_read"]
        + (cache_creation_tokens or 0) * rates["cache_creation"]
    ) / 1_000_000.0
    return round(total, 6)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_query(
    question: str,
    answer: str,
    model: str,
    session_id: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> None:
    """Log one Jack GPT turn to stdout (always) and Google Sheets (if configured).

    Never raises — all failures are swallowed and printed so the chat is
    never disrupted by logging issues.
    """
    try:
        record = {
            "timestamp_cn": datetime.now(CHINA_TZ).isoformat(timespec="seconds"),
            "user_email": st.session_state.get("user_email", ""),
            "user_name": st.session_state.get("user_name", ""),
            "session_id": session_id or "",
            "question": (question or "")[:MAX_QUESTION_LEN],
            "answer": (answer or "")[:MAX_ANSWER_LEN],
            "model": model,
            "input_tokens": int(input_tokens or 0),
            "output_tokens": int(output_tokens or 0),
            "cache_read_tokens": int(cache_read_tokens or 0),
            "cache_creation_tokens": int(cache_creation_tokens or 0),
            "cost_usd": _estimate_cost_usd(
                model,
                int(input_tokens or 0),
                int(output_tokens or 0),
                int(cache_read_tokens or 0),
                int(cache_creation_tokens or 0),
            ),
        }
    except Exception as exc:
        print(f"[JACK_GPT_LOG_ERROR] record build failed: {exc}", file=sys.stderr, flush=True)
        return

    # Sink 1: stdout/stderr (always)
    try:
        print(
            f"[JACK_GPT_LOG] {json.dumps(record, ensure_ascii=False)}",
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
            f"[JACK_GPT_SHEETS_ERROR] {type(exc).__name__}: {exc}",
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
    sheet_id = _get_secret("JACK_GPT_SHEET_ID")
    if not sheet_id:
        return  # not configured — that's fine

    client = _get_gspread_client()
    if client is None:
        return

    sh = client.open_by_key(sheet_id)
    tab_name = _get_secret("JACK_GPT_SHEET_TAB", "queries") or "queries"

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
        pass

    row = [record.get(h, "") for h in HEADERS]
    ws.append_row(row, value_input_option="USER_ENTERED")


@st.cache_resource(show_spinner=False)
def _get_gspread_client():
    """Return an authenticated gspread client, or None if not configured.

    Resolution order:
      1. `[jack_gpt_service_account]` TOML table — preferred when you want
         a dedicated GCP service account for Jack (full isolation).
      2. `[gcp_service_account]` TOML table — shared with Jerry. Works
         fine as long as the same service-account email has been added as
         Editor on both Jerry's and Jack's spreadsheets.

    Cached across reruns — credentials don't change at runtime.
    """
    if not _GSPREAD_AVAILABLE:
        return None
    try:
        sa_info = None
        try:
            sa_info = st.secrets.get("jack_gpt_service_account")
        except Exception:
            pass
        if not sa_info:
            try:
                sa_info = st.secrets.get("gcp_service_account")
            except Exception:
                pass
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
            f"[JACK_GPT_AUTH_ERROR] {type(exc).__name__}: {exc}",
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
