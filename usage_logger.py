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
from datetime import datetime, timezone

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _GSPREAD_AVAILABLE = True
except ImportError:
    _GSPREAD_AVAILABLE = False
    gspread = None  # type: ignore


MAX_QUESTION_LEN = 2000  # truncate per cell to keep Sheets responsive
HEADERS = [
    "timestamp_utc",
    "user_email",
    "user_name",
    "question",
    "model",
    "length",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_creation_tokens",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_query(
    question: str,
    model: str,
    length: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
) -> None:
    """Log one Jerry GPT turn to stdout (always) and Google Sheets (if configured).

    Never raises. All failures are swallowed and printed so the user's chat
    experience is never disrupted by logging issues.
    """
    try:
        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user_email": st.session_state.get("user_email", ""),
            "user_name": st.session_state.get("user_name", ""),
            "question": (question or "")[:MAX_QUESTION_LEN],
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
