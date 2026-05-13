"""Cookie-based session persistence for the Sales Toolkit.

The toolkit's login already sets st.session_state['authenticated']. The
problem: Streamlit's session_state lives only inside one WebSocket
connection. Refreshing the tab, or navigating to ?view=jerry_gpt with
target="_top", opens a new connection and wipes session_state — forcing
re-login.

This module adds a browser cookie that carries a signed session token
across reloads. On every Streamlit run, restore_session() checks the
cookie, verifies the signature, and re-hydrates session_state.

Security model:
- Token = "<user>:<expiry_unix>:<sha256_hmac_truncated>"
- Signature uses st.secrets["AUTH_SECRET"] (or env var AUTH_SECRET).
- An attacker who can read the user's cookie can impersonate them
  (same trust model as the existing shared SMTP-validated login —
  good enough for an internal sales tool, not for handling PII).
- Tokens expire after COOKIE_EXPIRY_DAYS so a leaked cookie is bounded.

If AUTH_SECRET isn't set, a built-in fallback secret is used. This works
but anyone with the source can forge tokens — set AUTH_SECRET in
secrets.toml for any non-trivial deployment.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta

import streamlit as st

try:
    import extra_streamlit_components as stx
    _STX_AVAILABLE = True
except ImportError:
    _STX_AVAILABLE = False


COOKIE_NAME = "stmx_auth"
COOKIE_EXPIRY_DAYS = 7
_FALLBACK_SECRET = "stmx-default-set-AUTH_SECRET-in-secrets-toml"


# ---------------------------------------------------------------------------
# Token signing / verification
# ---------------------------------------------------------------------------

def _get_secret() -> str:
    try:
        s = st.secrets.get("AUTH_SECRET")
        if s:
            return str(s)
    except Exception:
        pass
    return os.environ.get("AUTH_SECRET", _FALLBACK_SECRET)


def _sign(payload: str) -> str:
    """Truncated SHA-256 of payload + secret. Not full HMAC but adequate here."""
    secret = _get_secret()
    return hashlib.sha256(f"{payload}|{secret}".encode("utf-8")).hexdigest()[:24]


def _make_token(user: str) -> str:
    """Compose: 'user:expiry_unix:signature'."""
    expiry = int((datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)).timestamp())
    payload = f"{user}:{expiry}"
    return f"{payload}:{_sign(payload)}"


def _verify_token(token: str) -> str | None:
    """Return username if token is valid + non-expired, else None."""
    if not token or token.count(":") < 2:
        return None
    payload, sig = token.rsplit(":", 1)
    if _sign(payload) != sig:
        return None
    try:
        user, expiry_str = payload.rsplit(":", 1)
        expiry = int(expiry_str)
    except (ValueError, TypeError):
        return None
    if datetime.now().timestamp() > expiry:
        return None
    return user


# ---------------------------------------------------------------------------
# Cookie manager
# ---------------------------------------------------------------------------
#
# `stx.CookieManager(key=...)` is a Streamlit widget. Streamlit's rules:
#   - Cannot be wrapped in @st.cache_resource (raises CachedWidgetWarning).
#   - Cannot be instantiated twice in the same run with the same key.
#   - MUST be instantiated each run for the widget to be rendered/refreshed.
#
# Strategy: instantiate exactly once per run (inside `init()`), store the
# instance in st.session_state so any later helper (persist_login, logout)
# in the same run reuses it without re-creating the widget. The next run
# overwrites the stored instance with a fresh one.

_SESSION_CM_KEY = "_stmx_cookie_mgr"


def init() -> None:
    """Instantiate the cookie manager once for this Streamlit run.

    Call this near the top of app.py before any other auth helpers.
    Safe to call multiple times in one run (idempotent — only the first
    call actually creates the widget; subsequent calls are no-ops).
    """
    if not _STX_AVAILABLE:
        return
    # If something already instantiated the manager this run, leave it alone.
    # (This relies on the convention that `init()` is called once per run.
    # session_state persists across reruns, but the value we stash is itself
    # overwritten each call below, so stale references are fine.)
    if _SESSION_CM_KEY in st.session_state and st.session_state.get(
        "_stmx_cm_run_marker"
    ):
        return
    st.session_state[_SESSION_CM_KEY] = stx.CookieManager(key="stmx_cookie_mgr")
    st.session_state["_stmx_cm_run_marker"] = True


def _cm():
    """Return the run's cookie manager. Auto-inits if needed."""
    if _SESSION_CM_KEY not in st.session_state:
        init()
    return st.session_state.get(_SESSION_CM_KEY)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def restore_session() -> None:
    """Re-hydrate session_state from the auth cookie if valid.

    Call this once near the top of app.py, BEFORE checking
    st.session_state['authenticated']. Safe to call when already
    authenticated (no-op for the auth check; the cookie manager still
    initializes so persist_login/logout can use it later in the same run).
    """
    # Reset the per-run marker so init() will create a fresh CookieManager
    # widget for this run (Streamlit requires re-registration each run).
    st.session_state.pop("_stmx_cm_run_marker", None)
    st.session_state.pop(_SESSION_CM_KEY, None)
    init()

    if st.session_state.get("authenticated"):
        return
    cm = _cm()
    if cm is None:
        return
    token = cm.get(COOKIE_NAME)
    if not token:
        return
    user = _verify_token(token)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user_name"] = user
        # Re-derive leadership clearance from the restored user identity
        # so Jerry GPT enforces access control immediately after page reload.
        try:
            from login import resolve_leadership
            st.session_state["is_leadership"] = resolve_leadership(user)
        except Exception:
            st.session_state["is_leadership"] = False


def persist_login(user_name: str) -> None:
    """Called from login.py after credentials are validated.

    Writes the signed token to a browser cookie so the next refresh
    or tab navigation stays authenticated.
    """
    cm = _cm()
    if cm is None:
        return
    expires_at = datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
    try:
        cm.set(COOKIE_NAME, _make_token(user_name), expires_at=expires_at)
    except Exception:
        # Cookie write failed (unusual) — session still works for this tab
        pass


def logout() -> None:
    """Clear session state and the auth cookie."""
    cm = _cm()
    if cm is not None:
        try:
            cm.delete(COOKIE_NAME)
        except Exception:
            pass
    for key in ("authenticated", "user_name", "is_leadership"):
        st.session_state.pop(key, None)


def current_user() -> str | None:
    """Return the logged-in user's name, or None."""
    if not st.session_state.get("authenticated"):
        return None
    return st.session_state.get("user_name")
